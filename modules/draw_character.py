import math
import os

from PIL import Image

from .draw_common import myDraw, pic2b64
from .mytyping import Character, Index
from .util import ItemTrans


def cal_dest(im: Image.Image, center: int) -> int:
    """计算粘贴位置"""
    size = im.size
    return int(center - 0.5 * size[0])


class DrawCharacter(Character):
    """女武神列表绘制"""

    async def draw_chara(self, index: Index, qid: str = None) -> str:
        row_number = math.ceil(len(self.characters) / 3)
        card_chara = Image.new(
            mode="RGBA", size=(920, 20 + 320 * row_number), color=(236, 229, 216)
        )
        for no, valkyrie in enumerate(self.characters):
            with Image.open(
                os.path.join(os.path.dirname(__file__), "../assets/chara.png")
            ) as bg:
                blank = Image.new(mode="RGBA", size=bg.size, color=(236, 229, 216))
                md = myDraw(blank)
                img_backgroud = Image.open(
                    await md.get_net_img(
                        valkyrie.character.avatar.avatar_background_path
                    )
                )
                img_backgroud = img_backgroud.resize((190, 153))
                blank.alpha_composite(img_backgroud, dest=(46, 15))
                img_avatar = Image.open(
                    await md.get_net_img(
                        valkyrie.character.avatar.half_length_icon_path
                    )
                ).resize((172, 148))
                blank.alpha_composite(img_avatar, dest=(61, 19))
                blank.alpha_composite(bg)
                img_star = Image.open(
                    ItemTrans.star(valkyrie.character.avatar.star)
                ).resize((64, 54))
                blank.alpha_composite(img_star, dest=(48, 148))
                weapon = valkyrie.character.weapon
                bg_weapon = Image.open(
                    os.path.join(
                        os.path.dirname(__file__),
                        f"../assets/equipment_{weapon.max_rarity}.png",
                    )
                ).resize((75, 75))
                blank.alpha_composite(bg_weapon, dest=(215, 126))
                img_weapon = Image.open(await md.get_net_img(weapon.icon)).resize(
                    (72, 63)
                )
                blank.alpha_composite(img_weapon, dest=(215, 132))
                img_star = md.ImgResize(myDraw.star(weapon), height=27)
                blank.alpha_composite(img_star, dest=(cal_dest(img_star, 253), 182))
                for n, sti in enumerate(valkyrie.character.stigmatas):
                    if sti.id == 0:
                        img_none = Image.open(
                            os.path.join(
                                os.path.dirname(__file__), "../assets/equipment_0.png"
                            )
                        ).resize((75, 75))
                        blank.alpha_composite(img_none, dest=(35 + 76 * n, 223))
                    else:
                        bg_sti = Image.open(
                            os.path.join(
                                os.path.dirname(__file__),
                                f"../assets/equipment_{sti.max_rarity}.png",
                            )
                        ).resize((75, 75))
                        blank.alpha_composite(bg_sti, dest=(35 + 76 * n, 223))
                        img_sti = Image.open(await md.get_net_img(sti.icon)).resize(
                            (75, 65)
                        )
                        blank.alpha_composite(img_sti, dest=(35 + 76 * n, 228))
                        img_star = md.ImgResize(myDraw.star(sti), height=29)
                        blank.alpha_composite(
                            img_star, dest=(cal_dest(img_star, 73 + 76 * n), 279)
                        )
                font_lxj = myDraw.get_font("l", 26)
                md.text(
                    xy=(149, 176),
                    text=f"Lv.{valkyrie.character.avatar.level}",
                    fill="black",
                    font=font_lxj,
                    anchor="mt",
                )
                col = math.floor(no / 3)
                row = no % 3
                card_chara.alpha_composite(blank, dest=(10 + 300 * row, 10 + 320 * col))
                blank.close()
        # 创建抬头
        img_header = Image.open(
            os.path.join(os.path.dirname(__file__), "../assets/header.png")
        ).convert("RGBA")
        img_header = await myDraw.avatar(
            img_header, qid=qid, avatar_url=index.role.AvatarUrl, center=(460, 218)
        )
        dr = myDraw(img_header)
        dr.text(
            (900, 20),
            text=f"UID: {index.role.role_id}",
            fill="white",
            font=dr.get_font(size=30),
            anchor="rt",
        )
        dr.text(
            xy=(460, 460),
            text=index.role.nickname,
            fill=(0, 0, 0),
            font=dr.get_font("s", 40),
            anchor="mm",
        )
        dr.text(
            xy=(310, 552),
            text=str(index.role.level),
            fill=(133, 96, 61),
            font=dr.get_font(85, 40),
            anchor="lm",
        )
        dr.text(
            xy=(524, 552),
            text=ItemTrans.id2server(index.role.region),
            fill=(133, 96, 61),
            font=dr.get_font(85, 40),
            anchor="mm",
        )
        dr.text(
            xy=(368, 678),
            text=str(index.stats.armor_number),
            fill=(133, 96, 61),
            font=dr.get_font(85, 40),
            anchor="mm",
        )
        dr.text(
            xy=(842, 678),
            text=str(index.stats.sss_armor_number),
            fill=(133, 96, 61),
            font=dr.get_font(85, 40),
            anchor="mm",
        )
        # 组合
        with Image.new(
            "RGBA",
            (card_chara.size[0], card_chara.size[1] + img_header.size[1]),
            color=(236, 229, 216),
        ) as full_im:
            full_im.alpha_composite(img_header)
            full_im.alpha_composite(card_chara, (0, img_header.size[1]))
        return pic2b64(full_im, 100)
