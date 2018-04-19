import re
from discord.ext import commands
from utils.language import getlang

import utils.render as render
import utils.sqlite as sql
from utils.colors import pzone_colors, pzio_colors, pc_colors
from utils.logger import Log

log = Log(__name__)


class Canvas:
    def __init__(self, bot):
        self.bot = bot

    # =======================
    #          DIFF
    # =======================

    @commands.group(name="diff")
    async def diff(self, ctx):
        pass

    @staticmethod
    async def parse_diff(ctx, coords):
        if len(ctx.message.attachments) < 1:
            await ctx.send(getlang(ctx.guild.id, "bot.error.missing_attachment"))
            return
        filename = ctx.message.attachments[0].filename
        if filename[-4:].lower() != ".png":
            if filename[-4:].lower() == ".jpg" or filename[-5:].lower() == ".jpeg":
                await ctx.send(getlang(ctx.guild.id, "bot.error.jpeg"))
                return
            await ctx.send(getlang(ctx.guild.id, "bot.error.no_png"))
            return
        m = re.search('\(?(-?\d+), ?(-?\d+)\)?\s?#?(\d+)?', coords)
        if m is not None:
            x = int(m.group(1))
            y = int(m.group(2))
            att = ctx.message.attachments[0]
            zoom = int(m.group(3)) if m.group(3) is not None else 1
            zoom = max(1, min(zoom, 400 // att.width, 400 // att.height))
            return ctx, x, y, att, zoom

    @diff.command(name="pixelcanvas")
    async def diff_pixelcanvas(self, ctx, *, coordinates: str):
        args = await Canvas.parse_diff(ctx, coordinates)
        if args is not None:
            log.debug("Pixelcanvas diff invoked by {0.name}#{0.discriminator} (ID: {0.id}) in {1.name} (ID: {1.id})"
                      .format(ctx.author, ctx.guild))
            await render.diff(*args, render.fetch_pixelcanvas, pc_colors)

    @diff.command(name="pixelzio")
    async def diff_pixelzio(self, ctx, *, coordinates: str):
        args = await Canvas.parse_diff(ctx, coordinates)
        if args is not None:
            log.debug("Pixelzio diff invoked by {0.name}#{0.discriminator} (ID: {0.id}) in {1.name} (ID: {1.id})"
                      .format(ctx.author, ctx.guild))
            await render.diff(*args, render.fetch_pixelzio, pzio_colors)

    @diff.command(name="pixelzone")
    async def diff_pixelzone(self, ctx, *, coordinates: str):
        args = await Canvas.parse_diff(ctx, coordinates)
        if args is not None:
            log.debug("Pixelzone diff invoked by {0.name}#{0.discriminator} (ID: {0.id}) in {1.name} (ID: {1.id})"
                      .format(ctx.author, ctx.guild))
            await render.SIOConn().diff(*args)

    # =======================
    #        PREVIEW
    # =======================

    @commands.group(name="preview")
    async def preview(self, ctx):
        pass

    @staticmethod
    async def parse_preview(ctx, coords):
        m = re.search('(-?\d+), ?(-?\d+)/?\s?#?(\d+)?', coords)
        if m is not None:
            x = int(m.group(1))
            y = int(m.group(2))
            zoom = int(m.group(3)) if m.group(3) is not None else 1
            zoom = max(min(zoom, 16), 1)
            return ctx, x, y, zoom

    @preview.command(name="pixelcanvas")
    async def preview_pixelcanvas(self, ctx, *, coordinates: str):
        args = await Canvas.parse_preview(ctx, coordinates)
        if args is not None:
            log.debug("Pixelcanvas preview invoked by {0.name}#{0.discriminator} (ID: {0.id}) in {1.name} (ID: {1.id})"
                      .format(ctx.author, ctx.guild))
            await render.preview(*args, render.fetch_pixelcanvas)

    @preview.command(name="pixelzio")
    async def preview_pixelzio(self, ctx, *, coordinates: str):
        args = await Canvas.parse_preview(ctx, coordinates)
        if args is not None:
            log.debug("Pixelzio preview invoked by {0.name}#{0.discriminator} (ID: {0.id}) in {1.name} (ID: {1.id})"
                      .format(ctx.author, ctx.guild))
            await render.preview(*args, render.fetch_pixelzio)

    @preview.command(name="pixelzone")
    async def preview_pixelzone(self, ctx, *, coordinates: str):
        args = await Canvas.parse_preview(ctx, coordinates)
        if args is not None:
            log.debug("Pixelzone preview invoked by {0.name}#{0.discriminator} (ID: {0.id}) in {1.name} (ID: {1.id})"
                      .format(ctx.author, ctx.guild))
            await render.SIOConn().preview(*args)

    # =======================
    #        QUANTIZE
    # =======================

    @commands.group(name="quantize")
    async def quantize(self, ctx):
        pass

    @staticmethod
    async def check_attachment(ctx):
        if len(ctx.message.attachments) < 1:
            await ctx.send(getlang(ctx.guild.id, "bot.error.missing_attachment"))
            return False
        filename = ctx.message.attachments[0].filename
        if filename[-4:].lower() != ".png":
            if filename[-4:].lower() == ".jpg" or filename[-5:].lower() == ".jpeg":
                await ctx.send(getlang(ctx.guild.id, "bot.error.jpeg"))
                return False
            await ctx.send(getlang(ctx.guild.id, "bot.error.no_png"))
            return False
        return True

    @quantize.command(name="pixelcanvas")
    async def quantize_pixelcanvas(self, ctx):
        if await Canvas.check_attachment(ctx):
            log.debug("Pixelcanvas quantize invoked by {0.name}#{0.discriminator} (ID: {0.id}) in {1.name} (ID: {1.id})"
                      .format(ctx.author, ctx.guild))
            await render.quantize(ctx, ctx.message.attachments[0], pc_colors)

    @quantize.command(name="pixelzio")
    async def quantize_pixelzio(self, ctx):
        if await Canvas.check_attachment(ctx):
            log.debug("Pixelzio quantize invoked by {0.name}#{0.discriminator} (ID: {0.id}) in {1.name} (ID: {1.id})"
                      .format(ctx.author, ctx.guild))
            await render.quantize(ctx, ctx.message.attachments[0], pzio_colors)

    @quantize.command(name="pixelzone")
    async def quantize_pixelzone(self, ctx):
        if await Canvas.check_attachment(ctx):
            log.debug("Pixelzone quantize invoked by {0.name}#{0.discriminator} (ID: {0.id}) in {1.name} (ID: {1.id})"
                      .format(ctx.author, ctx.guild))
            await render.quantize(ctx, ctx.message.attachments[0], pzone_colors)

    @commands.command()
    async def repeat(self, ctx):
        async for msg in ctx.history(limit=50, before=ctx.message):
            regex = ctx.prefix \
                    + '(diff|preview) (pixelcanvas|pixelzio|pixelzone)(?: (-?\d+), ?(-?\d+)/?\s?#?(\d+)?)?'
            match = re.search(regex, msg.content)
            if match:
                cmd = match.group(1)
                sub_cmd = match.group(2)
                x = int(match.group(3))
                y = int(match.group(4))
                zoom = int(match.group(5)) if match.group(5) is not None else 1
                if cmd == "diff" and len(msg.attachments) > 0 and msg.attachments[0].filename[-4:].lower() == ".png":
                    att = msg.attachments[0]
                    zoom = max(1, min(zoom, 400 // att.width, 400 // att.height))
                    if sub_cmd == "pixelcanvas":
                        await render.diff(ctx, x, y, att, zoom, render.fetch_pixelcanvas, pc_colors)
                        return
                    elif sub_cmd == "pixelzio":
                        await render.diff(ctx, x, y, att, zoom, render.fetch_pixelzio, pzio_colors)
                        return
                    elif sub_cmd == "pixelzone":
                        await render.SIOConn().diff(ctx, x, y, att, zoom)
                        return
                if cmd == "preview":
                    zoom = max(1, min(16, zoom))
                    if sub_cmd == "pixelcanvas":
                        await render.preview(ctx, x, y, zoom, render.fetch_pixelcanvas)
                        return
                    elif sub_cmd == "pixelzio":
                        await render.preview(ctx, x, y, zoom, render.fetch_pixelzio)
                        return
                    elif sub_cmd == "pixelzone":
                        await render.SIOConn().preview(ctx, x, y, zoom)
                        return

            default_canvas = sql.select_guild_by_id(ctx.guild.id)['default_canvas']
            pc_match = re.search('(?:pixelcanvas\.io/)@(-?\d+),(-?\d+)/?(?:\s?#?(\d+))?', msg.content)
            pzio_match = re.search('(?:pixelz\.io/)@(-?\d+),(-?\d+)(?:\s?#?(\d+))?', msg.content)
            pzone_match = re.search('(?:pixelzone\.io/)\?p=(-?\d+),(-?\d+)(?:,(\d+))?(?:\s?#?(\d+))?', msg.content)
            prev_match = re.search('@\(?(-?\d+), ?(-?\d+)\)?(?: ?#(\d+))?', msg.content)
            diff_match = re.search('\(?(-?\d+), ?(-?\d+)\)?(?: ?#(\d+))?', msg.content)

            if pc_match is not None:
                x = int(pc_match.group(1))
                y = int(pc_match.group(2))
                zoom = int(pc_match.group(3)) if pc_match.group(3) is not None else 1
                zoom = max(min(zoom, 16), 1)
                await render.preview(ctx, x, y, zoom, render.fetch_pixelcanvas)
                return

            if pzio_match is not None:
                x = int(pzio_match.group(1))
                y = int(pzio_match.group(2))
                zoom = int(pzio_match.group(3)) if pzio_match.group(3) is not None else 1
                zoom = max(min(zoom, 16), 1)
                await render.preview(ctx, x, y, zoom, render.fetch_pixelzio)
                return

            if pzone_match is not None:
                x = int(pzone_match.group(1))
                y = int(pzone_match.group(2))
                if pzone_match.group(4) is not None:
                    zoom = int(pzone_match.group(4))
                elif pzone_match.group(3) is not None:
                    zoom = int(pzio_match.group(3))
                else:
                    zoom = 1
                zoom = max(min(zoom, 16), 1)
                await render.SIOConn().preview(ctx, x, y, zoom)
                return

            if prev_match is not None:
                x = int(prev_match.group(1))
                y = int(prev_match.group(2))
                zoom = int(prev_match.group(3)) if prev_match.group(3) is not None else 1
                zoom = max(min(zoom, 16), 1)
                if default_canvas == "pixelcanvas.io":
                    await render.preview(ctx, x, y, zoom, render.fetch_pixelcanvas)
                elif default_canvas == "pixelz.io":
                    await render.preview(ctx, x, y, zoom, render.fetch_pixelzio)
                elif default_canvas == "pixelzone.io":
                    await render.SIOConn().preview(ctx, x, y, zoom)
                return

            if diff_match is not None and len(msg.attachments) > 0 \
                    and msg.attachments[0].filename[-4:].lower() == ".png":
                att = msg.attachments[0]
                x = int(diff_match.group(1))
                y = int(diff_match.group(2))
                zoom = int(diff_match.group(3)) if diff_match.group(3) is not None else 1
                zoom = max(1, min(zoom, 400 // att.width, 400 // att.height))
                if default_canvas == "pixelcanvas.io":
                    await render.diff(ctx, x, y, att, zoom, render.fetch_pixelcanvas, pc_colors)
                elif default_canvas == "pixelz.io":
                    await render.diff(ctx, x, y, att, zoom, render.fetch_pixelzio, pzio_colors)
                elif default_canvas == "pixelzone.io":
                    await render.SIOConn().diff(ctx, x, y, att, zoom)
                return

            ctx.send(getlang(ctx.guild.id, "render.repeat_not_found"))


def setup(bot):
    bot.add_cog(Canvas(bot))