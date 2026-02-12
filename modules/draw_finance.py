import os

from PIL import Image

from .draw_common import myDraw, pic2b64
from .mytyping import FinanceInfo


class DrawFinance(FinanceInfo):
    """手账绘制"""

    def draw(self) -> str:
        with Image.open(
            os.path.join(os.path.dirname(__file__), "../assets/finance.png")
        ) as finance_bg:
            # 本月
            index = self.index
            dr = myDraw(finance_bg)
            font_6536 = myDraw.get_font()
            dr.text(
                xy=(375, 80),
                text=f"UID:{index.uid}",
                fill="black",
                font=font_6536,
                anchor="mm",
            )
            dr.text(
                xy=(375, 164),
                text=f"舰长的{index.month}月手账",
                fill="black",
                font=font_6536,
                anchor="mm",
            )
            dr.text(
                xy=(375, 245),
                text=f"截止至{index.date}",
                fill="black",
                font=font_6536,
                anchor="mm",
            )
            dr.text(
                xy=(161, 435),
                text=f"{index.month_hcoin}",
                fill="black",
                font=font_6536,
                anchor="lm",
            )
            dr.text(
                xy=(510, 435),
                text=f"{index.month_star:,}",
                fill="black",
                font=font_6536,
                anchor="lm",
            )
            if index.day_hcoin != 0 or index.day_star != 0:
                dr.text(
                    xy=(375, 550),
                    text=f"舰长今日已经获取{index.day_hcoin}水晶,{index.day_star}星石.",
                    fill="black",
                    font=font_6536,
                    anchor="mm",
                )
            else:
                dr.text(
                    xy=(375, 550),
                    text=f"舰长今日还没有收入哦.",
                    fill="black",
                    font=font_6536,
                    anchor="mm",
                )
            # 上月
            lastmonth = self.getLastMonthInfo
            font_6524 = myDraw.get_font(size=24)
            dr.text(
                xy=(375, 747),
                text=f"舰长的{lastmonth.month}月手账",
                fill="black",
                font=font_6536,
                anchor="mm",
            )
            dr.text(
                xy=(375, 841),
                text=f"{lastmonth.month_start.date()}至{lastmonth.month_end.date()}",
                fill="black",
                font=font_6536,
                anchor="mm",
            )
            dr.text(
                xy=(135, 1189),
                text=f"{lastmonth.month_hcoin:,}",
                fill="black",
                font=font_6524,
                anchor="lm",
            )
            dr.text(
                xy=(403, 1189),
                text=f"{lastmonth.month_star:,}",
                fill="black",
                font=font_6524,
                anchor="lm",
            )
            data = []
            for n, src in enumerate(lastmonth.group_by):
                data.append(src.percent)
                dr.text(
                    xy=(400, 940 + n * 49),
                    text=f"{src.name}",
                    fill="black",
                    font=font_6524,
                    anchor="lm",
                )
                dr.text(
                    xy=(665, 940 + n * 49),
                    text=f"{src.percent}%",
                    fill="black",
                    font=font_6524,
                    anchor="rm",
                )
            ring = dr.ring(data)
            finance_bg.alpha_composite(ring, dest=(37, 861))
            return pic2b64(finance_bg)
