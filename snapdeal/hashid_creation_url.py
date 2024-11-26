import hashlib


def create_md5_hash(input_string):
    md5_hash = hashlib.md5()
    md5_hash.update(input_string.encode('utf-8'))
    return md5_hash.hexdigest()




if __name__ == '__main__':
    url = 'https://www.snapdeal.com/product/x/665737749725'
    zipcode = '560001'
    hashid_delivery = create_md5_hash(str(url)+str(zipcode))

    hashid = create_md5_hash(url)
    print(f'main html pagesave: {hashid}')
    print(f'pricing json pagesave: {hashid_delivery}')