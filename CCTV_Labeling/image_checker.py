import sys

from controller.image_checker_controller import ImageCheckerController

if __name__ == '__main__':
    image_checker_controller = ImageCheckerController()
    sys.exit(image_checker_controller.run())