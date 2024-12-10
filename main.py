import io
from urllib.parse import unquote  # Importar para decodificar URL

import requests
from flask import Flask, request, send_file
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)

@app.route('/')
def index():
    # Captura o texto enviado na query string
    user_text = request.args.get("text", "Usuário")
    lunares_value = request.args.get("lunares", "0")
    avatar_url = request.args.get("avatar", None)

    # Decodificar o avatar_url
    if avatar_url:
        avatar_url = unquote(avatar_url)

    # Caminho do fundo (substitua por uma imagem do seu servidor ou URL pública)
    background_url = "https://i.postimg.cc/Z5HSFT5M/20241209-171441-0000.png"

    # Gerar a imagem com o texto
    image = create_profile_image(user_text, lunares_value, avatar_url, background_url)

    # Retornar a imagem como resposta
    return send_file(io.BytesIO(image), mimetype="image/png")


def create_profile_image(user_text, lunares_value, avatar_url, background_url):
    # Baixar o fundo
    response = requests.get(background_url)
    bg_image = Image.open(io.BytesIO(response.content)).convert("RGBA")

    # Criar objeto para desenhar na imagem
    draw = ImageDraw.Draw(bg_image)

    # Usar uma fonte padrão do Pillow
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    font_main = ImageFont.truetype(font_path, 40)
    font_lunares = ImageFont.truetype(font_path, 30)

    # Dimensões da imagem
    image_width, image_height = bg_image.size

    # Configurações de posição dos textos
    x_position_user = int(image_width * 0.33)
    y_position_user = int(image_height * 0.34)
    x_position_lunares = int(image_width * 0.03)
    y_position_lunares = int(image_height * 0.599)

    # Desenhar os textos
    draw.text((x_position_user, y_position_user), user_text, fill="white", font=font_main)
    draw.text((x_position_lunares, y_position_lunares), f"Lunares: {lunares_value}", fill="white", font=font_lunares)

    # Adicionar avatar circular, se disponível
    if avatar_url:
        try:
            avatar_response = requests.get(avatar_url)
            if avatar_response.status_code == 200:
                avatar_img = Image.open(io.BytesIO(avatar_response.content)).convert("RGBA")

                # Redimensionar o avatar
                avatar_size = (170, 170)  # Ajuste o tamanho conforme necessário
                avatar_img = avatar_img.resize(avatar_size, Image.LANCZOS)

                # Criar uma máscara circular
                mask = Image.new('L', avatar_size, 0)
                draw_mask = ImageDraw.Draw(mask)
                draw_mask.ellipse((0, 0) + avatar_size, fill=300)

                # Aplicar a máscara circular no avatar
                avatar_img.putalpha(mask)

                # Posicionar o avatar circular no fundo
                avatar_x = int(image_width * 0.075)
                avatar_y = int(image_height * 0.186)
                bg_image.paste(avatar_img, (avatar_x, avatar_y), avatar_img)
            else:
                print("Falha ao buscar o avatar")
        except Exception as e:
            print(f"Erro ao carregar o avatar circular: {e}")

    # Salvar a imagem em memória
    output = io.BytesIO()
    bg_image.save(output, format="PNG")
    output.seek(0)
    return output.getvalue()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
