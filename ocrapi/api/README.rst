API root:

    curl --header "Authorization: Token $OCR_SERVER_TOKEN" \
      http://192.168.1.150:8000/


List all orders:

    curl --header "Authorization: Token $OCR_SERVER_TOKEN" \
      http://192.168.1.150:8000/orders/


List user orders:

    curl --header "Authorization: Token $OCR_SERVER_TOKEN" \
      http://192.168.1.150:8000/orders/?user_uid=0


List of all images:

    curl --header "Authorization: Token $OCR_SERVER_TOKEN" \
      http://192.168.1.150:8000/images/


Single image details:

    curl --header "Authorization: Token $OCR_SERVER_TOKEN" \
      http://192.168.1.150:8000/images/11/


Upload image:

    curl --header "Authorization: Token $OCR_SERVER_TOKEN" \
      -F "user_uid=0" \
      -F "orders=$(<testdata/orders_1.json)" \
      -F "wholesalers={}" \
      -F "metrics={}" \
      -F "files=@testdata/1.jpg" \
      -F "files=@testdata/2.jpg" \
      http://192.168.1.101:8000/images/


Process a PDF for matching:

    curl --header "Authorization: Token $OCR_SERVER_TOKEN" \
      -F "user_uid=0" \
      -F "orders=$(<testdata/orders_2.json)" \
      -F "wholesalers={}" \
      -F "metrics={}" \
      -F "files=@testdata/1.pdf" \
      http://192.168.1.101:8000/images/


Upload structure:

    curl --header "Authorization: Token $OCR_SERVER_TOKEN" \
      -F "files=@testdata/1.jpg" \
      -F "files=@testdata/2.jpg" \
      http://192.168.1.101:8000/structure/
