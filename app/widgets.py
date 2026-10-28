from django.forms import ClearableFileInput


class CameraImageWidget(ClearableFileInput):
    """File input that also lets admin users take a photo with the device camera."""

    template_name = "app/widgets/camera_image.html"

    class Media:
        css = {"all": ("app/css/camera_widget.css",)}
        js = ("app/js/camera_widget.js",)

    def __init__(self, attrs=None):
        super().__init__({"accept": "image/*", **(attrs or {})})
