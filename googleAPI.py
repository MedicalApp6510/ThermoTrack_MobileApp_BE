def detect_text_uri(uri):
    """Detects text in the file located in Google Cloud Storage or on the Web."""
    from google.cloud import vision

    client = vision.ImageAnnotatorClient()
    image = vision.Image()
    image.source.image_uri = uri

    response = client.text_detection(image=image)
    texts = response.text_annotations

    # for text in texts:
    #    print(f'\n"{text.description}"')
    print(f'"{texts[1].description}"')

    if response.error.message:
        raise Exception(
            "{}\nFor more info on error messages, check: "
            "https://cloud.google.com/apis/design/errors".format(response.error.message)
        )
    return texts[1].description if texts else None


detect_text_uri("https://i.imgur.com/nyolbsP.jpeg") #345
# detect_text_uri("https://i.imgur.com/TxtSHdX.jpeg") #328但是应该是35.9
#
# detect_text_uri("https://i.imgur.com/mOSCBb8.jpeg")  #373
# detect_text_uri("https://i.imgur.com/1VkzeQO.jpeg")  #36.5
detect_text_uri("https://i.imgur.com/SaP2rHf.jpeg")  #35.9
