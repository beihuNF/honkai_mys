import os
from operator import attrgetter
from typing import List

from PIL import Image, ImageDraw

from .draw_common import myDraw, pic2b64
from .mytyping import AbyssReport, BattleFieldReport, FullInfo
from .util import ItemTrans


async def draw_abyss(aby: AbyssReport) -> Image.Image:
    if aby.type == "Greedy":
        bg_path = os.path.join(os.path.dirname(__file__), "../assets/abyss_greedy.png")
    else:
        bg_path = os.path.join(os.path.dirname(__file__), "../assets/abyss.png")
    with Image.open(bg_path) as im:
        dr = myDraw(im)
        with Image.new(mode="RGBA", size=im.size) as temp:
            for n, val in enumerate(aby.lineup):
                ava_bg = dr.ImgResize(
                    Image.open(
                        await dr.get_net_img(val.avatar_background_path)
                    ).convert("RGBA"),
                    1.5,
                )
                ava_icon = dr.ImgResize(
                    Image.open(await dr.get_net_img(val.icon_path)).convert("RGBA"),
                    0.72,
                )
                temp.alpha_composite(ava_bg, dest=(45 + n * 120, 108))
                temp.alpha_composite(ava_icon, dest=(45 + n * 120, 109))
            temp.alpha_composite(im)
            img_boss = dr.ImgResize(
                Image.open(await dr.get_net_img(aby.boss.avatar)), 1.26
            )
            if aby.elf is not None:
                img_elf = Image.open(await dr.get_net_img(aby.elf.avatar))
                img_elf = dr.ImgResize(img_elf, coe=0.74)
                img_elf_star = dr.ImgResize(
                    Image.open(ItemTrans.star(aby.elf.star, 1)), 0.755
                )
                temp.alpha_composite(img_elf, dest=(415, 110))
                temp.alpha_composite(img_elf_star, dest=(408, 172))
            for n, val in enumerate(aby.lineup):
                ava_star = dr.ImgResize(Image.open(ItemTrans.star(val.star)), 0.49)
                temp.alpha_composite(ava_star, dest=(23 + n * 120, 159))
            temp.alpha_composite(img_boss, dest=(700, 76))
            im = temp.copy()
        dr = myDraw(im)
        font_wh65 = myDraw.get_font(size=24)
        font_lxj = myDraw.get_font("l", 48)
        font_lxj_s = myDraw.get_font("l", 40)
        dr.text((39, 60), text=f"{aby.boss.name}", fill="white", font=font_wh65)
        if aby.type == "Greedy":
            if aby.floor == 10:
                dr.text(
                    xy=(938, 28),
                    text=f"{aby.floor}层{aby.score:,}",
                    fill="#0f9ed8",
                    font=font_lxj_s,
                    anchor="mm",
                )
            else:
                # TODO: 缺少数据，临时处理
                dr.text(
                    xy=(938, 28),
                    text=f"{aby.floor}层",
                    fill="#0f9ed8",
                    font=font_lxj,
                    anchor="mm",
                )
        else:
            dr.text(
                (865, 28),
                text=f"{aby.score:,}",
                fill="#0f9ed8",
                font=font_lxj,
                anchor="lm",
            )
        if aby.reward_type:
            # 有reward_type表明是低级区深渊
            abylevel = aby.level
            timescond = aby.time_second
            dr.text(
                xy=(580, 28),
                text=f"{ItemTrans.oldAbyssLevelChange(aby.reward_type)}",
                fill="white",
                font=font_wh65,
                anchor="lm",
            )
        else:
            abylevel = aby.level
            timescond = aby.updated_time_second
            dr.multiline_text(
                xy=(600, 153),
                text=f"段位: {ItemTrans.abyss_level(aby.settled_level)}\n排名: {str(aby.rank)}\n杯数: {aby.cup_number}({aby.settled_cup_number:+})",
                fill="white",
                font=font_wh65,
                anchor="lm",
            )
        dr.text(
            (39, 15),
            text=f"{ItemTrans.area(aby.area)}·{ItemTrans.abyss_level(abylevel)}·{ItemTrans.abyss_type(aby.type)}",
            fill="white",
            font=font_wh65,
        )
        dr.text(
            xy=(680, 90),
            text=f"结算时间:{timescond.astimezone().date()}",
            fill="#d4c18d",
            font=font_wh65,
            anchor="rb",
        )
        return im


async def draw_battlefield(bfs: BattleFieldReport) -> List[Image.Image]:
    ret: List[Image.Image] = []
    for bf in bfs.battle_infos:
        with Image.open(
            os.path.join(os.path.dirname(__file__), "../assets/bf.png")
        ) as bg:
            dr = myDraw(bg)
            img_boss = Image.open(await dr.get_net_img(bf.boss.avatar))
            bg.alpha_composite(img_boss, dest=(42, 0))
            for n, val in enumerate(bf.lineup):
                img_val = dr.ImgResize(
                    Image.open(await dr.get_net_img(val.background_path)), 0.77
                )
                bg.alpha_composite(img_val, dest=(0, 166 + 104 * n))
                img_star = dr.ImgResize(Image.open(ItemTrans.star(val.star)), 0.455)
                bg.alpha_composite(img_star, dest=(283, 222 + 104 * n))
            if bf.elf is not None:
                img_elf = dr.ImgResize(
                    Image.open(await dr.get_net_img(bf.elf.avatar)), 0.562
                )
                bg.alpha_composite(img_elf, dest=(124, 485))
                img_star = dr.ImgResize(
                    Image.open(ItemTrans.star(bf.elf.star, 1)), 0.44
                )
                bg.alpha_composite(img_star, dest=(195, 523))
            dr.text(
                xy=(170, 133),
                text=f"{bf.score:,}",
                fill="#f1bd31",
                font=myDraw.get_font("l", 48),
                anchor="mm",
            )
            ret.append(bg)
    return ret


class DrawIndex(FullInfo):
    """玩家卡片绘制"""

    async def draw_card(self, qid: str = None) -> str:
        weekr = self.weeklyReport
        if self.index.preference.is_god_war_unlock:
            bg_path = os.path.join(
                os.path.dirname(__file__), f"../assets/backgroud_godwar.png"
            )
        else:
            bg_path = os.path.join(
                os.path.dirname(__file__), f"../assets/backgroud_no_godwar.png"
            )
        bg = Image.open(bg_path).convert("RGBA")
        bg = await myDraw.avatar(bg, avatar_url=self.index.role.AvatarUrl, qid=qid)
        if weekr.favorite_character is not None:
            img_fav = Image.open(
                await myDraw.get_net_img(weekr.favorite_character.large_background_path)
            )
            bg.alpha_composite(img_fav, dest=(782, 367))
        font = myDraw.get_font("s", 48)
        font_6536 = myDraw.get_font()
        font_8548 = myDraw.get_font("85", 48)
        font_6532 = myDraw.get_font(size=32)
        font_6524 = myDraw.get_font(size=24)
        draw = myDraw(bg)
        draw.text(
            (1100, 20),
            text=f"UID:{self.index.role.role_id}",
            fill="white",
            font=font_6536,
            anchor="rt",
        )
        draw.text(
            xy=(562, 562),
            text=self.index.role.nickname,
            fill=(0, 0, 0),
            font=font,
            anchor="mm",
        )
        draw.text(
            xy=(390, 675),
            text=str(self.index.role.level),
            fill=(133, 96, 61),
            font=font_8548,
            anchor="lm",
        )
        draw.text(
            xy=(641, 677),
            text=ItemTrans.id2server(self.index.role.region),
            fill=(133, 96, 61),
            font=font_8548,
            anchor="mm",
        )

        # 深渊
        if self.index.stats.old_abyss is not None:
            draw.text(
                xy=(232, 821),
                text="量子奇点",
                fill=(133, 96, 61),
                font=font_6536,
                anchor="mm",
            )
            draw.text(
                xy=(232, 885),
                text=ItemTrans.abyss_level(self.index.stats.old_abyss.level_of_quantum),
                fill=(133, 96, 61),
                font=font_6532,
                anchor="mm",
            )
            draw.line(xy=[(310, 790), (310, 917)], fill=(161, 154, 129), width=0)
            draw.text(
                xy=(410, 821),
                text="量子流形",
                fill=(133, 96, 61),
                font=font_6536,
                anchor="mm",
            )
            draw.text(
                xy=(410, 885),
                text=ItemTrans.abyss_level(self.index.stats.old_abyss.level_of_greedy),
                fill=(133, 96, 61),
                font=font_6532,
                anchor="mm",
            )
        else:
            draw.text(
                xy=(310, 821),
                text="超弦空间",
                fill=(133, 96, 61),
                font=font_6536,
                anchor="mm",
            )
            draw.text(
                xy=(232, 885),
                text=ItemTrans.abyss_level(self.index.stats.new_abyss.level),
                fill=(133, 96, 61),
                font=font_8548,
                anchor="mm",
            )
            draw.text(
                xy=(410, 885),
                text=f"{self.index.stats.new_abyss.cup_number}杯",
                fill=(133, 96, 61),
                font=font_6532,
                anchor="mm",
            )
        # 战场
        draw.text(
            xy=(790, 821),
            text=ItemTrans.area(self.index.stats.battle_field_area),
            fill=(133, 96, 61),
            font=font_6536,
            anchor="mm",
        )
        if self.index.stats.battle_field_score != 0:
            draw.text(
                xy=(697, 885),
                text=f"{self.index.stats.battle_field_score:,}",
                fill=(133, 96, 61),
                font=font_6536,
                anchor="mm",
            )
            draw.text(
                xy=(880, 885),
                text=f"{self.index.stats.battle_field_ranking_percentage}%",
                fill=(133, 96, 61),
                font=font_8548,
                anchor="mm",
            )
        else:
            draw.text(
                xy=(790, 885),
                text="无数据",
                fill=(133, 96, 61),
                font=font_6532,
                anchor="mm",
            )
        # 数据总览
        draw.text(
            xy=(465, 1190),
            text=str(self.index.stats.active_day_number),
            fill=(133, 96, 61),
            font=font_8548,
            anchor="mm",
        )
        draw.text(
            xy=(465, 1305),
            text=str(self.index.stats.armor_number),
            fill=(133, 96, 61),
            font=font_8548,
            anchor="mm",
        )
        draw.text(
            xy=(465, 1420),
            text=str(self.index.stats.weapon_number),
            fill=(133, 96, 61),
            font=font_8548,
            anchor="mm",
        )
        draw.text(
            xy=(1010, 1190),
            text=str(self.index.stats.suit_number),
            fill=(133, 96, 61),
            font=font_8548,
            anchor="mm",
        )
        draw.text(
            xy=(1010, 1305),
            text=str(self.index.stats.sss_armor_number),
            fill=(133, 96, 61),
            font=font_8548,
            anchor="mm",
        )
        draw.text(
            xy=(1010, 1420),
            text=str(self.index.stats.stigmata_number),
            fill=(133, 96, 61),
            font=font_8548,
            anchor="mm",
        )
        # 往世乐土
        if self.index.preference.is_god_war_unlock:
            draw.text(
                xy=(307, 1645),
                text=str(self.index.stats.god_war_max_support_point),
                fill=(133, 96, 61),
                font=font_8548,
                anchor="mm",
            )
            draw.text(
                xy=(809, 1645),
                text=str(self.index.stats.god_war_max_challenge_score),
                fill=(133, 96, 61),
                font=font_8548,
                anchor="mm",
            )
            draw.text(
                xy=(307, 1789),
                text=str(self.index.stats.god_war_max_level_avatar_number),
                fill=(133, 96, 61),
                font=font_8548,
                anchor="mm",
            )
            draw.text(
                xy=(809, 1789),
                text=str(self.index.stats.god_war_extra_item_number),
                fill=(133, 96, 61),
                font=font_8548,
                anchor="mm",
            )
        # 舰长偏好
        data = [
            self.index.preference.battle_field,
            self.index.preference.abyss,
            self.index.preference.god_war,
            self.index.preference.open_world,
            self.index.preference.community,
            self.index.preference.main_line,
        ]
        if self.index.preference.is_god_war_unlock:
            bg = draw.radar(bg, data=data, center=(237, 2246), radius=164)
        else:
            data.pop(2)
            bg = draw.radar(bg, data=data, center=(237, 2246), radius=177)
        draw = ImageDraw.Draw(bg)
        draw.text(
            xy=(845, 2176),
            text=str(self.index.preference.comprehensive_score),
            font=font_8548,
            fill=(133, 96, 61),
            anchor="mm",
        )
        rating_image_path = ItemTrans.rate2png(
            self.index.preference.comprehensive_rating
        )
        rating_image = Image.open(rating_image_path).convert("RGBA")
        bg.alpha_composite(rating_image, dest=(782, 2300))
        # 深渊战报
        if self.newAbyssReport is not None:
            abyss = self.newAbyssReport
        else:
            abyss = self.latestOldAbyssReport
            abyss.reports.sort(key=attrgetter("time_second"), reverse=True)
        if len(abyss.reports) == 0:
            bg.alpha_composite(
                Image.open(
                    os.path.join(os.path.dirname(__file__), "../assets/no-data.png")
                ),
                dest=(379, 2767),
            )
        for n, reports in enumerate(abyss.reports):
            abyss_card = await draw_abyss(reports)
            bg.alpha_composite(abyss_card, dest=(48, 2622 + n * 230))
            if n >= 2:
                break
        # 战场战报
        if self.battleFieldReport.reports:
            bfr = self.battleFieldReport.reports[0]
            ims = await draw_battlefield(bfr)
            for n, bfcard in enumerate(ims):
                bg.alpha_composite(bfcard, dest=(39 + 355 * n, 3542))
            draw.text(
                xy=(562, 3506),
                text=f"{ItemTrans.area(bfr.area)}\t{bfr.ranking_percentage}%\t{bfr.score:,}",
                fill=(133, 96, 61),
                font=font_6536,
                anchor="mm",
            )
            draw.text(
                xy=(1110, 3530),
                text=f"结算时间:{bfr.time_second.astimezone().date()}",
                fill="gray",
                font=font_6524,
                anchor="rb",
            )
        else:
            bg.alpha_composite(
                Image.open(
                    os.path.join(os.path.dirname(__file__), "../assets/no-data2.png")
                ),
                dest=(398, 3678),
            )
        # bg.show()

        return pic2b64(bg, quality=100)
