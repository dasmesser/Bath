from numpy.lib.type_check import imag
from data_providers import data_pluggin
from utils import constants
import urllib2
import json
import unicodedata
import threading
import Queue

class PhylopicPluggin(data_pluggin.DataPluggin):
    #TODO constructor
    
    def get_first_image_specific_implementation(self, species):
        #returns the url of the first image of the species found in the source
        lock = threading.Lock()
        queue = Queue.Queue()
        threadNumber = min(10, len(species))

        for i in range(threadNumber) :
            t = GetImageThread(self.img_list, self.err_list, lock, queue, False, i)
            t.setDaemon(True)
            t.start()

        #populate the queue
        for sp in species :
            queue.put(sp)
        queue.join()
    
    def get_all_images_specific_implementation(self, species):
        #returns the url of the first image of the species found in the source
        lock = threading.Lock()
        queue = Queue.Queue()
        threadNumber = min(10, len(species))

        for i in range(threadNumber) :
            t = GetImageThread(self.img_list, self.err_list, lock, queue, True, i)
            t.setDaemon(True)
            t.start()

        #populate the queue
        for sp in species :
            queue.put(sp)
        queue.join()

class GetImageThread(threading.Thread):

    def __init__(self, images, errors, lock, queue, multiple_results, id=0):
        threading.Thread.__init__(self)
        self.images = images
        self.errors = errors
        self.lock = lock
        self.queue = queue
        self.multiple_results = multiple_results
        self.id = id

    def get_species_uid(self, species):
        buffer = species.replace(' ', '+')     
        url = 'http://phylopic.org/api/a/name/search?text=' + buffer + '&options=illustrated'
        json_uid = ''
        
        i = 0
        #Se intenta completar 3 veces la conexion
        while True:
            try:
                json_uid = json.load(urllib2.urlopen(url))
                break
            except URLError:
                if i < 3:
                    i = i + 1
                else:
                    return (False, constants.CONNECTION_ERROR)
            except:
                return (False, constants.JSON_ERROR)
        
        if json_uid['success'] and not(len(json_uid['result']) == 0):
            return (True, json_uid)
        else:
            return (False, constants.NO_SPECIES_BY_PROVIDED_NAME) 

    def run(self):
        """

        :return:
        """
        while True:
            species = self.queue.get()
            self.lock.acquire()
            if not species in self.images : # Species was not processed before.
                self.lock.release()
                print("Starting process for {}".format(species))
                try :
                    url = None
                    image_url = None
                    (return_status, json_uid) = self.get_species_uid(species)

                    if not(return_status) :
                        with self.lock:
                            self.errors[species] = json_uid
                            self.images[species] = image_url
                        self.queue.task_done()
                        continue
                    else:
                        element_list = json_uid['result']
                        uids = []

                        for element in element_list:
                            #Check if the element is illustrated
                            if element.has_key('illustrated') and element['illustrated'] == True:
                                #for some reason the uid comes in unicode type instead of str,
                                #so a conversion is needed
                                uid = element['canonicalName']['uid']
                                uid = unicodedata.normalize('NFKD', uid).encode('ascii', 'ignore')
                                uids.append(uid)

                        if len(uids) == 0 : #No images found for species.
                            with self.lock :
                                self.errors[species] = constants.NO_IMAGES_FOR_SPECIES
                                self.images[species] = image_url
                            self.queue.task_done()
                            continue # To the main while
                        else:
                            img_list = []
                        
                            for uid in uids :
                                url = 'http://phylopic.org/api/a/name/' + uid + '/images?options=pngFiles'
                                json_img = ''

                                i = 0
                                #The connection will be tried up to 3 times
                                while True:
                                    try:
                                        json_img = json.load(urllib2.urlopen(url))
                                        break
                                    except URLError:
                                        if i < 3:
                                            i = i + 1
                                        else:
                                            with self.lock:
                                                self.errors[species] = constants.CONNECTION_ERROR
                                                self.images[species] = image_url
                                            self.queue.task_done()
                                            json_img = ''
                                            break
                                    except:
                                            with self.lock:
                                                self.errors[species] = constants.JSON_ERROR
                                                self.images[species] = image_url
                                            self.queue.task_done()
                                            json_img = ''
                                            break
                                
                                if json_img == '':
                                    continue
                                            
                                if json_img.has_key('success') and json_img['success'] == True:
                                    element_list = json_img['result']['same']

                                    for element in element_list:
                                        pngFiles = element['pngFiles']
                                        for inner_element in pngFiles:
                                            #for each image there are always versions in different sizes (64, 128, 256, 512 and 1024).
                                            image_url = 'http://phylopic.org' + unicodedata.normalize('NFKD', inner_element['url']).encode('ascii', 'ignore')
                                            
                                            if self.multiple_results:
                                                if not(image_url in img_list) :
                                                    img_list.append(image_url)
                                            else:
                                                break
                                        
                                        if self.multiple_results:
                                            continue
                                        elif not(image_url is None) :
                                            break
                                            
                                if self.multiple_results:
                                    continue
                                elif not(image_url is None):
                                    break

                            if ((self.multiple_results and not(img_list))
                                or (not(self.multiple_results) and image_url is None)) : #No image found, load an error
                                with self.lock :
                                    self.errors[species] = constants.NO_IMAGES_FOR_SPECIES
                                    self.images[species] = image_url
                                self.queue.task_done()
                                continue # To the main while
                            else :
                                print("Endind task, success {}".format(species))
                                with self.lock:
                                    self.errors[species] = None
                                    if self.multiple_results :
                                        self.images[species] = img_list
                                    else :
                                        self.images[species] = image_url
                                self.queue.task_done()
                                continue # To the main while
                except Exception as ex :
                    with self.lock:
                        self.errors[species] = constants.NO_IMAGES_FOR_SPECIES
                        self.images[species] = image_url #Should be None
                    self.queue.task_done()
            else :
                self.lock_release()
                self.queue.task_done()
