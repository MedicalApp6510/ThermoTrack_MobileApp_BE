# Import necessary libraries
import sys

def detect_text_uri(uri):
    """Detects text in the file located in Google Cloud Storage or on the Web."""
    from google.cloud import vision

    client = vision.ImageAnnotatorClient()
    image = vision.Image()
    image.source.image_uri = uri

    response = client.text_detection(image=image)
    texts = response.text_annotations

    print(f'"{texts[1].description}"')

    if response.error.message:
        raise Exception(
            "{}\nFor more info on error messages, check: "
            "https://cloud.google.com/apis/design/errors".format(response.error.message)
        )
    return texts[1].description if texts else None


if __name__ == "__main__":
    # Check if the correct number of command-line arguments is provided
    if len(sys.argv) != 2:
        print("Usage: python main.py <image_url>")
        sys.exit(1)

    # Get the image URL from command-line arguments
    image_url = sys.argv[1]

    # Process the image and print the result
    try:
        result = detect_text_uri(image_url)
    except Exception as e:
        print("Error:", e)