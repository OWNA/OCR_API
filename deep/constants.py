import os

OUTPUT_DIR = 'out/deep'

# Image generator parameters
TEXT_GENERATOR_OUPUT_SIZE = 28
NUMBER_GENERATOR_OUPUT_SIZE = 12
ABSOLUTE_MAX_STRING_LEN = 16
IMAGE_WIDTH = 192
IMAGE_HEIGHT = 64
MINIBATCH_SIZE = 32
EVAL_SIZE = 2048

# Training params
WORDS_PER_EPOCH = 12800
WORD_LIST_SIZE = 640000

# The following command was used to obtain the list of fonts
# fc-list | grep google-fonts | awk -F '[:,]' '{print $2}' | sort | uniq
# awk '{gsub(/ /, "", $1); printf "\"%s\",", $1}'

FONTS_DIRECTORY = '/usr/share/fonts/truetype/google-fonts'
DISABLED_FONTS = [
    'Corben-Bold.ttf',
    'AdobeBlank-Regular.ttf',
    'AksaraBaliGalang-Regular.ttf',
    'Angkor.ttf',
    'Battambang-Bold.ttf',
    'Battambang-Regular.ttf',
    'Bayon.ttf',
    'Bokor.ttf',
    'Chenla.ttf',
    'Content-Bold.ttf',
    'Content-Regular.ttf',
    'cwTeXFangSong-zhonly.ttf',
    'cwTeXHei-zhonly.ttf',
    'cwTeXKai-zhonly.ttf',
    'cwTeXMing-zhonly.ttf',
    'cwTeXYen-zhonly.ttf',
    'Dangrek.ttf',
    'DroidKufi-Bold.ttf',
    'DroidKufi-Regular.ttf',
    'DroidNaskh-Bold.ttf',
    'DroidNaskh-Regular.ttf',
    'DroidSansEthiopic-Bold.ttf',
    'DroidSansEthiopic-Regular.ttf',
    'DroidSansJapanese.ttf',
    'DroidSansTamil-Bold.ttf',
    'DroidSansTamil-Regular.ttf',
    'DroidSansThai-Bold.ttf',
    'DroidSansThai-Regular.ttf',
    'DroidSerifThai-Bold.ttf',
    'DroidSerifThai-Regular.ttf',
    'Fasthand-Regular.ttf',
    'Freehand.ttf',
    'Hannari-Regular.ttf',
    'InknutAntiqua-Black.ttf',
    'InknutAntiqua-Bold.ttf',
    'InknutAntiqua-ExtraBold.ttf',
    'InknutAntiqua-Light.ttf',
    'InknutAntiqua-Medium.ttf',
    'InknutAntiqua-Regular.ttf',
    'InknutAntiqua-SemiBold.ttf',
    'jsMath-cmbx10.ttf',
    'jsMath-cmex10.ttf',
    'jsMath-cmmi10.ttf',
    'jsMath-cmr10.ttf',
    'jsMath-cmsy10.ttf',
    'jsMath-cmti10.ttf',
    'Kantumruy-Bold.ttf',
    'Kantumruy-Light.ttf',
    'Kantumruy-Regular.ttf',
    'KarlaTamilInclined-Bold.ttf',
    'KarlaTamilInclined-Regular.ttf',
    'KarlaTamilUpright-Bold.ttf',
    'KarlaTamilUpright-Regular.ttf',
    'KdamThmor-Regular.ttf',
    'Khmer.ttf',
    'Kokoro-Regular.ttf',
    'Koulen.ttf',
    'LaoMuangDon-Regular.ttf',
    'LaoMuangKhong-Regular.ttf',
    'LaoSansPro-Regular.ttf',
    'Lohit-Bengali.ttf',
    'Lohit-Devanagari.ttf',
    'Lohit-Tamil.ttf',
    'Metal.ttf',
    'Moul.ttf',
    'Moulpali.ttf',
    'MyanmarSansPro-Regular.ttf',
    'Nikukyu-Regular.ttf',
    'Nokora-Bold.ttf',
    'Nokora-Regular.ttf',
    'OdorMeanChey.ttf',
    'Phetsarath-Bold.ttf',
    'Phetsarath-Regular.ttf',
    'Ponnala-Regular.ttf',
    'Preahvihear.ttf',
    'Redacted-Regular.ttf',
    'RedactedScript-Bold.ttf',
    'RedactedScript-Regular.ttf',
    'Siemreap.ttf',
    'Sitara-Bold.ttf',
    'Sitara-BoldItalic.ttf',
    'Sitara-Italic.ttf',
    'Sitara-Regular.ttf',
    'Souliyo-Regular.ttf',
    'Sumana-Bold.ttf',
    'Sumana-Regular.ttf',
    'Suwannaphum.ttf',
    'Taprom.ttf',
    'Yinmar-Regular.ttf'
]

FONTS = set(os.listdir(FONTS_DIRECTORY))
FONTS = FONTS.difference(set(DISABLED_FONTS))
FONTS = list(FONTS)
