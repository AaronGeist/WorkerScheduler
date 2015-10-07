# coding=utf-8
__author__ = 'yzhou7'


class SystemInitializer:
    def __init__(self):
        pass

    # entry for system init
    @staticmethod
    def initialize():
        pass
        # SystemInitializer.createDir()
        # SystemInitializer.createFiles()

    # @staticmethod
    # def createDir():
    #     if not os.path.exists(Constants.DATA_DIR):
    #         os.makedirs(Constants.DATA_DIR)
    #
    # @staticmethod
    # def createFiles():
    #     SystemInitializer.createBuyerFile()
    #     SystemInitializer.createSellerFile()
    #
    # @staticmethod
    # def createBuyerFile():
    #     if not os.path.exists(Constants.BUYER_FILE_PATH):
    #         file = open(Constants.BUYER_FILE_PATH, "w")
    #         file.close()
    #
    # @staticmethod
    # def createSellerFile():
    #     if not os.path.exists(Constants.SELLER_FILE_PATH):
    #         file = open(Constants.SELLER_FILE_PATH, "w")
    #         file.close()
