from PIL import Image
def createThumbnail(orig):
    pimg = Image.open(orig)
    pimg.thumbnail((200, 200), Image.NEAREST)
    return pimg