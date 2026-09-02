"""Byte fallback: why a BPE tokenizer charges some alphabets per byte.

Every number on screen is real and reproducible with two lines of tiktoken or
tokenizers code: hello is one GPT-2 token; ọkọ̀ is nine, one per UTF-8 byte,
because the merges that would compress it were never learned; የኢትዮጵያ is
eighteen. The measured premiums at the end come from this repository's sweep
of 204 FLORES-200 languages.

Render (Manim CE lives only in the ember venv on this machine; needs TinyTeX
on PATH for real LaTeX):

  PATH="$HOME/Library/TinyTeX/bin/universal-darwin:/usr/local/bin:$PATH" \\
  ../ember/.venv/bin/manim -qh assets/manim_fallback.py ByteFallback
"""

from manim import *

GROUND = "#141019"
INK = "#F0EBE3"
DIM = "#9A8FA6"
GOLD = "#E8B04B"
CORAL = "#E8654F"
TEAL = "#4FBFA8"
VIOLET = "#9F7FE8"


def token_boxes(pieces, colours, y=0.0, size=34, box_pad=0.16):
    """A row of boxed token pieces."""
    group = VGroup()
    for piece, colour in zip(pieces, colours):
        t = Text(piece, font_size=size, color=INK)
        box = SurroundingRectangle(t, color=colour, buff=box_pad,
                                   corner_radius=0.08, stroke_width=2.5)
        group.add(VGroup(box, t))
    group.arrange(RIGHT, buff=0.12).move_to([0, y, 0])
    return group


class ByteFallback(Scene):
    def construct(self):
        self.camera.background_color = GROUND

        title = Text("The tokenizer tax", font_size=44, color=INK)
        sub = Text("why the same meaning costs some languages ten times more",
                   font_size=22, color=DIM).next_to(title, DOWN, buff=0.3)
        self.play(FadeIn(title, shift=UP * 0.3), run_time=1.1)
        self.play(FadeIn(sub), run_time=0.6)
        self.wait(1.2)
        self.play(FadeOut(title), FadeOut(sub), run_time=0.6)

        # ------------------------------------------------ hello: one token
        h1 = Text("hello", font_size=48, color=INK).move_to(UP * 2.2)
        self.play(FadeIn(h1), run_time=0.7)
        hb = token_boxes(["hello"], [TEAL], y=1.0, size=40)
        c1 = Text("1 token", font_size=26, color=TEAL).next_to(hb, RIGHT,
                                                               buff=0.5)
        self.play(TransformFromCopy(h1, hb), FadeIn(c1), run_time=1.0)
        note = Text("five letters the tokenizer has seen a billion times,\n"
                    "merged all the way into a single unit",
                    font_size=20, color=DIM, line_spacing=0.9)
        note.next_to(hb, DOWN, buff=0.5)
        self.play(FadeIn(note), run_time=0.7)
        self.wait(1.5)
        self.play(FadeOut(h1), FadeOut(hb), FadeOut(c1), FadeOut(note),
                  run_time=0.6)

        # ------------------------------------------- oko: nine byte tokens
        w = Text("ọkọ̀", font_size=52, color=INK).move_to(UP * 2.4)
        gloss = Text("vehicle, in Yoruba: four visible characters",
                     font_size=20, color=DIM).next_to(w, DOWN, buff=0.22)
        self.play(FadeIn(w), FadeIn(gloss), run_time=0.8)

        bytes_row = token_boxes(
            ["E1", "BB", "8D", "6B", "E1", "BB", "8D", "CC", "80"],
            [CORAL] * 9, y=0.6, size=24, box_pad=0.12)
        blab = Text("its nine UTF-8 bytes", font_size=20, color=DIM)
        blab.next_to(bytes_row, DOWN, buff=0.3)
        self.play(TransformFromCopy(w, bytes_row), FadeIn(blab), run_time=1.2)
        self.wait(0.8)

        tok_row = token_boxes(["·"] * 9, [CORAL] * 9, y=-0.9, size=24,
                              box_pad=0.12)
        tlab = Text("9 tokens. One per byte. No merges were ever learned "
                    "for this script.",
                    font_size=21, color=CORAL).next_to(tok_row, DOWN, buff=0.35)
        self.play(TransformFromCopy(bytes_row, tok_row), FadeIn(tlab),
                  run_time=1.2)
        compare = Text("hello: 1 token.   ọkọ̀: 9 tokens.",
                       font_size=26, color=INK).to_edge(DOWN, buff=0.6)
        self.play(FadeIn(compare), run_time=0.8)
        self.wait(2.0)
        self.play(FadeOut(w), FadeOut(gloss), FadeOut(bytes_row), FadeOut(blab),
                  FadeOut(tok_row), FadeOut(tlab), FadeOut(compare),
                  run_time=0.7)

        # ------------------------------------------------- what that means
        head = Text("Same benchmark, same 1,012 sentences, every language",
                    font_size=25, color=INK).to_edge(UP, buff=0.6)
        self.play(FadeIn(head), run_time=0.7)

        rows = [("English", 1.00, TEAL), ("Swahili", 1.49, GOLD),
                ("Yoruba", 2.17, GOLD), ("Amharic", 5.78, CORAL)]
        bars = VGroup()
        for i, (name, prem, colour) in enumerate(rows):
            y = 1.4 - i * 0.95
            lab = Text(name, font_size=26, color=INK)
            lab.move_to([-4.6, y, 0], aligned_edge=RIGHT)
            bar = Rectangle(width=prem * 1.35, height=0.5, fill_color=colour,
                            fill_opacity=0.9, stroke_width=0)
            bar.move_to([-3.9 + prem * 1.35 / 2, y, 0])
            val = Text(f"{prem:.2f}x", font_size=24, color=colour)
            val.next_to(bar, RIGHT, buff=0.25)
            bars.add(VGroup(lab, bar, val))
        cap = Text("tokens paid for identical content, GPT-4o tokenizer",
                   font_size=20, color=DIM).to_edge(DOWN, buff=1.15)
        self.play(LaggedStart(*[FadeIn(b) for b in bars], lag_ratio=0.25),
                  FadeIn(cap), run_time=2.2)
        cost = Text("the premium is the price multiplier, the latency "
                    "multiplier, and the context shrinkage, all at once",
                    font_size=20, color=DIM).next_to(cap, DOWN, buff=0.18)
        self.play(FadeIn(cost), run_time=0.8)
        self.wait(2.2)
        self.play(FadeOut(bars), FadeOut(head), FadeOut(cap), FadeOut(cost),
                  run_time=0.7)

        # ---------------------------------------------- the design choice
        final = VGroup(
            Text("Under NLLB's tokenizer, built for 200 languages,",
                 font_size=26, color=INK),
            Text("Amharic pays 1.29x. Yoruba pays 1.48x.",
                 font_size=30, color=TEAL),
            Text("The tax is not a property of the language.",
                 font_size=26, color=INK),
            Text("It is a property of the training data.",
                 font_size=30, color=GOLD),
        ).arrange(DOWN, buff=0.4)
        self.play(LaggedStart(*[FadeIn(m, shift=UP * 0.15) for m in final],
                              lag_ratio=0.4), run_time=2.6)
        self.wait(2.2)
        self.play(FadeOut(final), run_time=0.7)

        end = Text("owóorí", font_size=52, color=GOLD)
        end2 = Text("the tokenizer tax, measured across 204 languages",
                    font_size=21, color=DIM).next_to(end, DOWN, buff=0.32)
        self.play(FadeIn(end, shift=UP * 0.2), FadeIn(end2), run_time=1.1)
        self.wait(1.6)
