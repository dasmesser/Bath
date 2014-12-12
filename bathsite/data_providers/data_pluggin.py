import abc
import threading

class DataPluggin(object):
    __metaclass__=abc.ABCMeta

    def __init__(self):
        self.img_list = dict()
        self.err_list = dict()
    
    def get_first_image(self, species):
        self.get_first_image_specific_implementation(species)
    
    @abc.abstractmethod
    def get_first_image_specific_implementation(self, species):
        #returns the url of the first image of the species found in the source
        return
    
    def get_all_images(self, species):
        self.get_all_images_specific_implementation(species)
    
    @abc.abstractmethod
    def get_all_images_specific_implementation(self, species):
        #returns a list of all the urls for the species found in the source
        return
        
