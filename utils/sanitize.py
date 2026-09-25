from html_sanitizer.sanitizer import DEFAULT_SETTINGS, Sanitizer

# CKEditor5 rich-text fields (CGUItem.description, FAQItem.description) are edited
# through the "default" CKEDITOR_5_CONFIGS toolbar: bold, italic, underline,
# numberedList, bulletedList, link, removeFormat, sourceEditing.
#
# We sanitize the text before save and before displaying it to safegarde against code injection
_RICH_TEXT_SETTINGS = {
    **DEFAULT_SETTINGS,
    "tags": DEFAULT_SETTINGS["tags"] | {"u"},
}

_rich_text_sanitizer = Sanitizer(_RICH_TEXT_SETTINGS)


def sanitize_rich_text(value):
    """Strip unsafe HTML from a CKEditor5 rich-text value, keeping safe formatting."""
    if not value:
        return value
    return _rich_text_sanitizer.sanitize(value)
