# Sample Captions: Vintage Mechanical Keyboard LoRA

## Trigger Word

**`vintagekb`** -- used as the activation token at the start of every caption.

## Caption Style

Natural language captions describing the subject, composition, and key aesthetic details. Each caption should:
1. Start with the trigger word
2. Identify the keyboard type/model if known
3. Describe the case color and keycap colors
4. Note the layout and any distinctive features
5. Describe the setting/background briefly
6. Mention lighting or mood if relevant

---

## Example Captions

### 1. IBM Model M -- Classic Full Shot
```
vintagekb, a vintage IBM Model M mechanical keyboard with beige case and light gray keycaps, blue sub-legends on the function row, buckling spring switches, full-size layout with numpad, coiled PS/2 cable, sitting on a dark wooden desk, warm indoor lighting
```

### 2. Cherry G80-3000 -- Studio Product Shot
```
vintagekb, a Cherry G80-3000 mechanical keyboard with cream beige case, white and gray doubleshot keycaps, red escape key accent, Cherry MX switches, full-size layout, straight cable, photographed on a clean white background, soft studio lighting
```

### 3. Apple Extended Keyboard II -- Environmental Shot
```
vintagekb, an Apple Extended Keyboard II with platinum gray beige case and matching keycaps, Alps switches, full-size layout with Apple command keys, ADB cable, next to a matching beige Apple mouse and Macintosh SE CRT monitor, vintage office desk setup, natural window light
```

### 4. Commodore 64 -- Close-Up Detail
```
vintagekb, close-up detail shot of a Commodore 64 keyboard showing brown and beige keycaps with colorful function keys in orange red blue and green, printed legends, integrated keyboard design, visible key texture and wear marks, shallow depth of field, macro photography
```

### 5. Terminal Keyboard -- Wyse WY-85
```
vintagekb, a Wyse WY-85 terminal keyboard with warm beige case and ivory keycaps, green and orange color-coded modifier keys, Cherry MX black switches, full-size layout with extra function keys, attached coiled cable, sitting on a metal desk in an office environment, fluorescent overhead lighting
```

### 6. Modern Board with Retro Keycap Set
```
vintagekb, a modern custom mechanical keyboard with GMK Retro keycap set, beige and cream colorway with red and blue accent keys, Cherry profile doubleshot ABS keycaps, mounted on a black aluminum 65-percent layout case, on a beige deskmat, warm desk lamp lighting
```

### 7. Collection Shot -- Multiple Vintage Boards
```
vintagekb, a collection of vintage mechanical keyboards arranged on a table, including an IBM Model M, a Cherry G80, and a DEC terminal keyboard, all featuring beige and cream cases with various keycap colors, overhead flat lay photograph, even lighting, retro computing aesthetic
```

### 8. NEC Keyboard -- Side Profile
```
vintagekb, side profile view of a vintage NEC mechanical keyboard with beige case showing the thick chunky housing and tall keycap profile, cream colored keycaps with dark legends, visible key stems, DIN connector cable, against a neutral gray background, product photography style
```

---

## Caption Variations for Training Diversity

The same image concept should use varied phrasing across the dataset to prevent the model from memorizing rigid sentence patterns:

**Formal/descriptive:**
```
vintagekb, a vintage mechanical keyboard featuring a beige ABS case and colorful PBT keycaps in cream, red, and blue, full-size layout, photographed on a desk
```

**Casual/concise:**
```
vintagekb, beige retro keyboard with colorful keycaps on a wooden desk, warm lighting
```

**Detail-focused:**
```
vintagekb, extreme close-up of vintage keyboard keycaps showing dye-sublimated legends on beige PBT plastic, Cherry profile, visible key texture and slight yellowing from age
```

This variation in caption length and style helps the LoRA respond well to both short prompts and detailed descriptions.

---

## Regularization Image Captions (Optional)

If using regularization images (generic modern keyboards), caption them WITHOUT the trigger word:

```
a modern mechanical keyboard with black case and RGB backlit keycaps, tenkeyless layout, on a gaming desk
```

```
a white wireless mechanical keyboard with pastel keycaps, compact 65-percent layout, minimalist desk setup
```

These teach the model what a "normal" keyboard looks like, so the trigger word specifically activates the vintage beige aesthetic.
