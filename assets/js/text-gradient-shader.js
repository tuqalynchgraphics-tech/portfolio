/**
 * Text Gradient Shader — gooey glow / melt version (vanilla JS)
 * -------------------------------------------------
 * Matches a "liquid glow" text style: a crisp colored core word with
 * a soft blurred halo behind it, where the halo visually melts and
 * fuses with the cursor as it moves nearby (the classic SVG "goo"
 * filter technique: blur + a sharpened alpha threshold makes
 * separate blurry shapes fuse into one liquid blob when they
 * overlap).
 *
 * No WebGL — just real DOM text (so it stays crisp and selectable-
 * looking) plus an SVG filter and a cursor-following blob.
 *
 * Usage:
 *   import { TextGradientShader } from "./text-gradient-shader.js";
 *
 *   new TextGradientShader(document.getElementById("hero"), {
 *     text: "GRADIENT",
 *     coreColor: "#e8262f",
 *     haloColor: "#ff8fc7",
 *     fontFamily: "Inter, sans-serif",
 *     fontSize: 96,
 *     fontWeight: 800,
 *     haloBlur: 16,       // px blur on the halo layer
 *     gooStrength: 22,    // higher = sharper liquid-merge edges
 *     blobSize: 90,        // px diameter of the cursor blob
 *     ease: 0.15,          // 0-1, cursor-follow smoothing
 *   });
 *
 * The container needs an explicit width (CSS) so both text layers
 * wrap identically; height can be auto.
 */

let filterCounter = 0

export class TextGradientShader {
    constructor(container, options = {}) {
        this.container = container
        this.options = {
            text: options.text ?? "Your Text Here",
            fontFamily: options.fontFamily ?? "Inter, sans-serif",
            fontSize: options.fontSize ?? 96,
            fontWeight: options.fontWeight ?? 800,
            coreColor: options.coreColor ?? "#e8262f",
            haloColor: options.haloColor ?? "#ff8fc7",
            haloBlur: options.haloBlur ?? 16,
            gooStrength: options.gooStrength ?? 22,
            blobSize: options.blobSize ?? 90,
            ease: options.ease ?? 0.15,
        }

        this.filterId = `tgs-goo-${filterCounter++}`
        this.target = { x: -9999, y: -9999 }
        this.current = { x: -9999, y: -9999 }
        this.active = false
        this.raf = null

        this._buildDom()
        this._bindEvents()
        this._loop()
    }

    _buildDom() {
        const o = this.options
        const c = this.container

        c.style.position = c.style.position || "relative"

        c.innerHTML = `
            <svg width="0" height="0" style="position:absolute">
                <defs>
                    <filter id="${this.filterId}">
                        <feGaussianBlur in="SourceGraphic" stdDeviation="${o.haloBlur}" result="blur" />
                        <feColorMatrix in="blur" mode="matrix"
                            values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 ${o.gooStrength} -${o.gooStrength / 2}"
                            result="goo" />
                        <feComposite in="goo" in2="goo" operator="atop" />
                    </filter>
                </defs>
            </svg>

            <div class="tgs-goo-layer" style="
                position:relative;
                filter:url(#${this.filterId});
            ">
                <div class="tgs-halo-text" style="
                    width:100%;
                    text-align:center;
                    font-family:${o.fontFamily};
                    font-size:${o.fontSize}px;
                    font-weight:${o.fontWeight};
                    color:${o.haloColor};
                    line-height:1.05;
                    margin:0;
                    user-select:none;
                ">${o.text}</div>

                <div class="tgs-cursor-blob" style="
                    position:absolute;
                    top:0; left:0;
                    width:${o.blobSize}px;
                    height:${o.blobSize}px;
                    margin-left:-${o.blobSize / 2}px;
                    margin-top:-${o.blobSize / 2}px;
                    border-radius:50%;
                    background:${o.haloColor};
                    opacity:0;
                    pointer-events:none;
                    will-change:transform, opacity;
                "></div>
            </div>

            <div class="tgs-core-text" style="
                position:absolute;
                inset:0;
                width:100%;
                text-align:center;
                font-family:${o.fontFamily};
                font-size:${o.fontSize}px;
                font-weight:${o.fontWeight};
                color:${o.coreColor};
                line-height:1.05;
                margin:0;
                pointer-events:none;
                user-select:none;
            ">${o.text}</div>
        `

        this.blob = c.querySelector(".tgs-cursor-blob")
        this.haloText = c.querySelector(".tgs-halo-text")
        this.coreText = c.querySelector(".tgs-core-text")
    }

    _bindEvents() {
        this._onMove = (e) => {
            const rect = this.container.getBoundingClientRect()
            this.target.x = e.clientX - rect.left
            this.target.y = e.clientY - rect.top
            if (!this.active) {
                this.active = true
                this.blob.style.opacity = "1"
            }
        }
        this._onLeave = () => {
            this.active = false
            this.blob.style.opacity = "0"
        }

        this.container.addEventListener("pointermove", this._onMove)
        this.container.addEventListener("pointerleave", this._onLeave)
    }

    _loop() {
        const render = () => {
            this.current.x += (this.target.x - this.current.x) * this.options.ease
            this.current.y += (this.target.y - this.current.y) * this.options.ease
            this.blob.style.transform = `translate(${this.current.x}px, ${this.current.y}px)`
            this.raf = requestAnimationFrame(render)
        }
        this.raf = requestAnimationFrame(render)
    }

    /** Update the displayed text without recreating the instance. */
    setText(text) {
        this.options.text = text
        this.haloText.textContent = text
        this.coreText.textContent = text
    }

    /** Update core/halo colors. */
    setColors(coreColor, haloColor) {
        this.options.coreColor = coreColor
        this.options.haloColor = haloColor
        this.coreText.style.color = coreColor
        this.haloText.style.color = haloColor
        this.blob.style.background = haloColor
    }

    /** Remove listeners, stop the animation loop, clear the DOM. */
    destroy() {
        if (this.raf) cancelAnimationFrame(this.raf)
        this.container.removeEventListener("pointermove", this._onMove)
        this.container.removeEventListener("pointerleave", this._onLeave)
        this.container.innerHTML = ""
    }
}
