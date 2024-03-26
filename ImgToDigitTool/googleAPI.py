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


# detect_text_uri("https://i.imgur.com/nyolbsP.jpeg") #345
# detect_text_uri("https://i.imgur.com/mOSCBb8.jpeg")  #373
detect_text_uri("https://i.imgur.com/1VkzeQO.jpeg")  #36.5
