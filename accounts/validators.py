import os.path

from django.core.exceptions import ValidationError


def allow_only_images_validator(value):
    ext = os.path.splitext(value.name)[1]  # cover-images.jpg ['cover-images', 'jpg]
    # print(ext)
    valid_extensions = [
        ".png",
        ".jpg",
        ".jpe",
        ".jpeg",
    ]
    if not ext.lower() in valid_extensions:
        raise ValidationError(
            "Unsupported file Extension. Allowed Extension: " + str(valid_extensions)
        )
