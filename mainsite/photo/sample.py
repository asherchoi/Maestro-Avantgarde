import service_app

tf = service_app.StyleTransfer('/home/thchoi/jupyter_root/maestro/mainsite/media/photo/content_img/nature.jpg',
				'/home/thchoi/jupyter_root/maestro/mainsite/media/photo/style_img/wall.jpg',
				'/home/thchoi/jupyter_root/maestro/mainsite/media/photo/result_img/xxxxxxx.jpg')
tf.transfer()
