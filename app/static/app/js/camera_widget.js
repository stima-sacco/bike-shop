"use strict";

(function () {
  function setFile(input, file) {
    const transfer = new DataTransfer();
    transfer.items.add(file);
    input.files = transfer.files;
    input.dispatchEvent(new Event("change", { bubbles: true }));
  }

  function initWidget(widget) {
    const input = widget.querySelector('input[type="file"]:not([data-camera-fallback])');
    const fallback = widget.querySelector("[data-camera-fallback]");
    const panel = widget.querySelector("[data-camera-panel]");
    const video = widget.querySelector("[data-camera-video]");
    const preview = widget.querySelector("[data-camera-preview]");
    const status = widget.querySelector("[data-camera-status]");
    let stream = null;
    let facingMode = "environment";

    function stopCamera() {
      if (stream) {
        stream.getTracks().forEach((track) => track.stop());
        stream = null;
      }
      panel.hidden = true;
    }

    async function startCamera() {
      stopCamera();
      status.textContent = "";
      stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode, width: { ideal: 1920 }, height: { ideal: 1080 } },
        audio: false,
      });
      video.srcObject = stream;
      panel.hidden = false;
    }

    widget.querySelector("[data-camera-open]").addEventListener("click", async () => {
      // getUserMedia only works on HTTPS or localhost; fall back to the
      // native camera picker (mobile browsers) when it is unavailable.
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        fallback.click();
        return;
      }
      try {
        await startCamera();
      } catch (error) {
        status.textContent = "Camera unavailable (" + error.name + "). Choose a file instead.";
        fallback.click();
      }
    });

    widget.querySelector("[data-camera-switch]").addEventListener("click", async () => {
      facingMode = facingMode === "environment" ? "user" : "environment";
      try {
        await startCamera();
      } catch (error) {
        status.textContent = "Could not switch camera (" + error.name + ").";
      }
    });

    widget.querySelector("[data-camera-cancel]").addEventListener("click", stopCamera);

    widget.querySelector("[data-camera-capture]").addEventListener("click", () => {
      const canvas = document.createElement("canvas");
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      canvas.getContext("2d").drawImage(video, 0, 0);
      canvas.toBlob((blob) => {
        const name = "camera-" + new Date().toISOString().replace(/[:.]/g, "-") + ".jpg";
        setFile(input, new File([blob], name, { type: "image/jpeg" }));
        stopCamera();
      }, "image/jpeg", 0.9);
    });

    fallback.addEventListener("change", () => {
      if (fallback.files.length) {
        setFile(input, fallback.files[0]);
      }
    });

    input.addEventListener("change", () => {
      const file = input.files[0];
      if (preview.src) {
        URL.revokeObjectURL(preview.src);
      }
      if (file) {
        preview.src = URL.createObjectURL(file);
        preview.hidden = false;
        status.textContent = "Selected: " + file.name;
      } else {
        preview.hidden = true;
        status.textContent = "";
      }
    });
  }

  // Tracked in JS rather than a data attribute, because inline rows added via
  // "Add another" are cloned from a template row and would copy the attribute.
  const initialised = new WeakSet();

  function initAll(root) {
    root.querySelectorAll("[data-camera-widget]").forEach((widget) => {
      if (!initialised.has(widget)) {
        initialised.add(widget);
        initWidget(widget);
      }
    });
  }

  document.addEventListener("DOMContentLoaded", () => initAll(document));
  document.addEventListener("formset:added", (event) => initAll(event.target));
})();
