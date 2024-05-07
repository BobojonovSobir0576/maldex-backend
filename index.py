from ftplib import FTP


def get_data_from_ftp():
    ftp = FTP()
    ftp.connect('static.xindaorussia.ru')
    ftp.login(user='maldex.ru', passwd='IR5XKKxKWR7JVA7A')

    filename = 'production.xml'
    with open('category.xml', 'wb') as file:
        ftp.retrbinary(f'RETR {filename}', file.write)

    filename = 'PrintData.xml'
    with open('product.xml', 'wb') as file:
        ftp.retrbinary(f'RETR {filename}', file.write)

    ftp.quit()
    print('File downloaded successfully')


if __name__ == "__main__":
    get_data_from_ftp()
