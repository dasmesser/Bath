from django.test import TestCase
from django.test import Client
from utils import constants

class Tests(TestCase):
    def setUp(self):
        self.c = Client()

    def ping_tests(self):
        #Ping test
        response = self.c.get('/ping/')
        self.assertEqual(response.status_code, 200)
        
        #Index
        response = self.c.get('/')
        self.assertEqual(response.status_code, 200)
        
        #Ete test
        response = self.c.get('/test')
        self.assertEqual(response.status_code, 200)
        
        #Phylopic single image
        response = self.c.get('/result/?input=(((Walrus,%20Homo_sapiens)%20(Black_bear,%20Giant_panda)),%20(fox))&data_source=Phylopic')
        self.assertEqual(response.status_code, 200)
        
        #Phylopic multiple image
        response = self.c.get('/multiple_results/?input=(((Walrus,%20Homo_sapiens)%20(Black_bear,%20Giant_panda)),%20(fox))&data_source=Phylopic')
        self.assertEqual(response.status_code, 200)
        
        #EoL single image
        response = self.c.get('/result/?input=(((Walrus,%20Homo_sapiens)%20(Black_bear,%20Giant_panda)),%20(fox))&data_source=Encyclopedia%20of%20life')
        self.assertEqual(response.status_code, 200)
        
        #EoL multiple image
        response = self.c.get('/multiple_results/?input=(((Walrus,%20Homo_sapiens)%20(Black_bear,%20Giant_panda)),%20(fox))&data_source=Encyclopedia%20of%20life')
        self.assertEqual(response.status_code, 200)
        
    def destructive_tests(self):
        #Homo sapiens separated by a space instead of a _
        response = self.c.get('/result/?input=(((Walrus,%20Homo sapiens)%20(Black_bear,%20Giant_panda)),%20(fox))&data_source=Phylopic')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, constants.SEPARATED_BY_SPACE_ERROR)
        
        #Incorrect Newick tree format
        response = self.c.get('/result/?input=((Walrus,%20Homo_sapiens)%20(Black_bear,%20Giant_panda)),%20(fox))&data_source=Phylopic')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, constants.NEWICK_TREE_FORMAT_ERROR)
        
        #No data source selected
        response = self.c.get('/result/?input=(((Walrus,%20Homo_sapiens)%20(Black_bear,%20Giant_panda)),%20(fox))&data_source=')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, constants.NO_PLUGGIN_SELECTED)
        
        #Invalid data source
        response = self.c.get('/result/?input=(((Walrus,%20Homo_sapiens)%20(Black_bear,%20Giant_panda)),%20(fox))&data_source=Not_A_Valid_Data_Source')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, constants.PLUGGIN_NOT_AVAILABLE)
        
        #No Newick tree
        response = self.c.get('/result/?input=&data_source=Phylopic')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, constants.NO_NEWICK_TREE)
    
    def regression_tests(self):
        #Phylopic single image regresion
        response = self.c.get('/result/?input=(((Walrus,%20Homo_sapiens)%20(Black_bear,%20Giant_panda)),%20(fox))&data_source=Phylopic')
        self.assertEqual(response.status_code, 200)
        self.assertTrue((response.content.find('c089caae-43ef-4e4e-bf26-973dd4cb65c5') != -1) 
        and (response.content.find('5a5dafa2-6388-43b8-a15a-4fd21cd17594') != -1)
        and (response.content.find('4b1f7a58-8713-4d6e-a130-4c8a1ac2f749') != -1)
        and (response.content.find('20da6c7c-2584-4cee-921b-ebd09384567b') != -1))
        
        #Phylopic multiple image regresion
        response = self.c.get('/multiple_results/?input=(((Walrus,%20Homo_sapiens)%20(Black_bear,%20Giant_panda)),%20(fox))&data_source=Phylopic')
        self.assertEqual(response.status_code, 200)
        #First, check if all the images were found
        self.assertTrue((response.content.find('c089caae-43ef-4e4e-bf26-973dd4cb65c5.256.png') != -1) 
        and (response.content.find('9c6af553-390c-4bdd-baeb-6992cbc540b1.512.png') != -1)
        and (response.content.find('2b4c32f6-99d0-43ba-9180-8013aa5bccd2.256.png') != -1)
        and (response.content.find('20da6c7c-2584-4cee-921b-ebd09384567b.512.png') != -1)
        and (response.content.find('51b1b6e4-129d-41a6-bbbd-c3fab459c25f.256.png') != -1))
        #Second, check there where no repeated images
        self.assertTrue((response.content.count('c089caae-43ef-4e4e-bf26-973dd4cb65c5.64.png') == 1)
        and (response.content.count('16cfde1b-d577-4de8-82b9-62b760aacba5.64.png') == 1))
        
        
        
        
        