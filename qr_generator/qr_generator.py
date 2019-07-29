import qrcode

class QRGenerator:

    @staticmethod
    def generate_qr_image(text, path):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(text)
        qr.make(fit=True)
        image_binary = qr.make_image()

        with open(path, 'wb') as img_tmp_file:
            image_binary.save(img_tmp_file, 'PNG')
