'''
base on Leon. A. Gatys, Alexander S. Ecker, Matthias Bethge, "A Neural Algorithm of Artistic Style", arXiv: 1508.06576
HUFS information communication engineering systhesis design class
made by 1team(avant-garde) 2017. 11. 3
'''

import time, math, sys
import numpy as np
from scipy.optimize import minimize
from scipy.misc import imread, imsave, imresize

import keras.backend as K
from keras.applications import vgg16, vgg19
from keras.applications.imagenet_utils import preprocess_input

CONTENT_IMAGE_FILEPATH = './img/chicago.jpg'
STYLE_IMAGE_FILEPATH = './img/thescream.jpg'
RESULT_IMAGE_FILEPATH = './img/result.jpg'


class StyleTransfer():
	def __init__(self, content_image_filepath, style_image_filepath, result_image_filepath):
		self.content_image_filepath = content_image_filepath
		self.style_image_filepath = style_image_filepath
		self.result_image_filepath = result_image_filepath
		self.alpha_content = 0.001
		self.beta_style = 1
		self.iterations = 100
		self.iteration = 0
		self.cnn_model = vgg16.VGG16(include_top = False) #not using 3 fully connected layers
		self.content_layer = 'block5_conv1'
		self.style_layers = ['block1_conv1', 'block2_conv1', 'block3_conv1', 'block4_conv1', 'block5_conv1']
		self.optimization_method = 'CG'
		self.layers = self.all_layers()
		self.get_filters_response = K.function(inputs=[self.cnn_model.layers[0].input],
                                             outputs=[self.cnn_model.get_layer(t).output for t in self.layers])

	def transfer(self):
		tic = time.time()
		print('==========step 1: pre processing image==========')
		self.read_content_img()
		self.read_style_img()

		print('============step 2: get loss fuctions===========')
		self.content_loss()
		self.style_loss()
		self.total_loss()

		print('==========step 3: optimize total loss===========')
		self.get_loss_gradient()
		self.make_noise_image()
		self.optimize()

		print('=========step 4: post processing image==========')
		self.redirect()
        
		toc = time.time()
		print('Total elapsed %.2f' %(toc-tic))
		
	def all_layers(self):
		if self.content_layer not in self.style_layers:
			layers = self.style_layers + [self.content_layer]
		else:
			layers = self.style_layers
		return layers
	

	def read_content_img(self):
		self.content_image = imread(self.content_image_filepath)
		self.content_image_shape = (self.content_image.shape[0], self.content_image.shape[1], 3) #
		self.e_image_shape = (1,) + self.content_image_shape
		self.content_pre = self.pre_process_image(self.content_image.reshape(self.e_image_shape).astype(K.floatx()))
		print('> Loading content image: %s (%dx%d)' % (self.content_image_filepath, self.content_pre.shape[2], self.content_pre.shape[1]))
		self.content_filters_responses = self.get_filters_response([self.content_pre]) #many thing?
		#print(self.content_filters_responses)
		self.content_representations = K.variable(value=self.content_filters_responses[self.layers.index(self.content_layer)])
		#print(self.content_representations)

	def read_style_img(self):
		self.style_image = imread(self.style_image_filepath)
		print('> Loading style image: %s (%dx%d)' % (self.style_image_filepath, self.style_image.shape[1], self.style_image.shape[0]))
		if (self.style_image.shape[0] != self.content_pre.shape[1]) or (self.style_image.shape[1] != self.content_pre.shape[2]):
			print('> Resizing style image to match content image  size: (%dx%d)' % (self.content_pre.shape[2], self.content_pre.shape[1]))
			self.style_image = imresize(self.style_image, size=(self.content_pre.shape[1], self.content_pre.shape[2]), interp='lanczos')
			print(self.e_image_shape)
			self.style_pre = self.pre_process_image(self.style_image.reshape(self.e_image_shape).astype(K.floatx()))
		self.style_filters_responses = self.get_filters_response([self.style_pre])
		#print(self.style_filters_responses)
		self.style_representations = [self.gram_matrix(o) for o in self.style_filters_responses] #style representation define by filters correlation
		#print(self.style_filters_responses)


    
	def content_loss(self):
		self.content_loss_function = 0.5 * K.sum(K.square(self.content_representations - self.cnn_model.get_layer(self.content_layer).output))
		print('> Complete define content loss function')

	def style_loss(self):
		self.style_loss_function = 0.0
		style_loss_function_weight = 1.0 / float(len(self.style_layers))
		for i, style_layer in enumerate(self.style_layers):
			N = self.style_filters_responses[i].shape[3]
			M = self.style_filters_responses[i].shape[1] * self.style_filters_responses[i].shape[2] 
			self.style_loss_function += (style_loss_function_weight *
			(1.0 / (4.0 * (N ** 2.0) * (M ** 2.0))) *
			K.sum(K.square(self.style_representations[i] - self.gram_matrix(self.cnn_model.get_layer(style_layer).output))))
		print('> Complete define style loss function')

	def total_loss(self):
		self.total_loss = (self.alpha_content * self.content_loss_function) + (self.beta_style * self.style_loss_function)
		cnn_inputs = [self.cnn_model.get_layer(l).output for l in self.layers]
		cnn_inputs.append(self.cnn_model.layers[0].input)
		self.total_loss_function = K.function(inputs=cnn_inputs, outputs=[self.total_loss])
		print('> Complete define total loss function')
	
	def get_loss_gradient(self):
		loss_gradient = K.gradients(loss=self.total_loss, variables=[self.cnn_model.layers[0].input])
		self.loss_function_gradient = K.function(inputs=[self.cnn_model.layers[0].input], outputs=loss_gradient)
		print('> Complete define loss gradient function')

	def make_noise_image(self):
		self.noise_image = self.content_pre.copy()
		print('> Make noise image based content image')
		

	def optimize(self):
		print('> Starting optimazation with %s method' %self.optimization_method)
		minimize(fun=self.loss, x0=self.noise_image.flatten(), jac=self.loss_gradient, callback= self.callback, method=self.optimization_method)

	def loss(self, image):
		outputs = self.get_filters_response([image.reshape(self.e_image_shape).astype(K.floatx())])
		outputs.append(image.reshape(self.e_image_shape).astype(K.floatx()))
		loss = self.total_loss_function(outputs)[0]
		print('Loss: %.2f' % loss)
		return loss


	def loss_gradient(self, image):
		return np.array(self.loss_function_gradient([image.reshape(self.e_image_shape).astype(K.floatx())])).astype('float64').flatten()

	def callback(self, image):
		self.iteration += 1
		if self.iteration == self.iterations + 1:
			print('Complete style transfer')
			self.iteration = 100
			self.save_image(image)
			sys.exit(0)
		self.noise_image = image.copy()
		print('Optimization step: %d/%d' % (self.iteration, self.iterations))
		#self.save_image(image)



	def gram_matrix(self, filters):
		c_filters = K.batch_flatten(K.permute_dimensions(K.squeeze(filters, axis=0), pattern=(2, 0, 1)))
		return K.dot(c_filters, K.transpose(c_filters))

	def pre_process_image(self, image):
		return preprocess_input(image)

	def postprocessing_img(self, image):
		image[:, :, :, 0] += 103.939
		image[:, :, :, 1] += 116.779
		image[:, :, :, 2] += 123.68
		return np.clip(image[:, :, :, ::-1], 0, 255).astype('uint8')[0]

	def save_image(self, image):
		imsave(self.result_image_filepath + str(self.iteration) + '.jpg', self.postprocessing_img(image.reshape(self.e_image_shape).copy()))

	def redirect(self):
		return

if __name__ == '__main__':
	styler = StyleTransfer(CONTENT_IMAGE_FILEPATH, STYLE_IMAGE_FILEPATH, RESULT_IMAGE_FILEPATH)
	styler.transfer() 
