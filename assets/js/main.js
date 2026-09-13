/* Tuqa Lynch — portfolio interactions */
(function () {
  "use strict";
  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* =====================================================================
     Preloader — black screen, "Tuqa Lynch" slides up into the masthead's
     own slot, then the overlay inverts to the site's colours and fades to
     reveal the page underneath.
     ===================================================================== */
  // A refresh mid-scroll otherwise restores the old scroll position (the
  // <head> inline script already does this ASAP to avoid a flash; repeated
  // here since some browsers re-apply scroll restoration after load).
  if ("scrollRestoration" in history) history.scrollRestoration = "manual";
  window.scrollTo(0, 0);

  var preload = document.getElementById("preload");
  if (preload) {
    if (reduced) {
      preload.remove();
    } else {
      document.documentElement.style.overflow = "hidden";
      requestAnimationFrame(function () {
        requestAnimationFrame(function () { preload.classList.add("run"); });
      });
      setTimeout(function () { preload.classList.add("invert"); }, 950);
      setTimeout(function () {
        preload.classList.add("done");
        window.scrollTo(0, 0);
        document.documentElement.style.overflow = "";
      }, 1450);
      setTimeout(function () { preload.remove(); }, 2000);
    }
  }

  /* =====================================================================
     Animated name(s).
     Any element with data-words builds "T"/"uqa" style spans — first letter
     kept, the rest become .hl spans. By default the .hl letters fade out
     where they sit 2s after load (a slow left-to-right sweep), leaving just
     the initials; hovering (or focusing / tapping) fades them back in. The
     topbar's mini mark is the same system at a smaller size, just already
     collapsed from the start (data-collapse-delay="0") — it's meant to read
     as a shrunken version of the big masthead, not its own separate thing.
     Every fresh load (or a plain back-navigation, which is a fresh load
     here too) replays this from scratch — nothing makes it "stick" open.
     ===================================================================== */
  var kernCanvas = document.createElement("canvas").getContext("2d");
  var noHover = window.matchMedia("(hover: none)").matches;

  var buildMark = function (mark) {
    if (mark.dataset.built) return;
    mark.dataset.built = "1";
    var i = 0;
    mark.dataset.words.split(",").forEach(function (w) {
      var wordEl = document.createElement("span");
      wordEl.className = "mark-word";
      w.split("").forEach(function (ch, idx) {
        var s = document.createElement("span");
        if (idx === 0) {
          s.className = "keep";
          s.textContent = ch;
        } else {
          s.className = "hl";
          s.appendChild(document.createTextNode(ch));   // fixed-font strut (transparent)
          var gi = document.createElement("i");
          gi.textContent = ch;
          s.appendChild(gi);                            // the visible revealed glyph
          s.setAttribute("aria-hidden", "true");
          s.style.setProperty("--i", i++);
        }
        wordEl.appendChild(s);
      });
      mark.appendChild(wordEl);
    });

    // The revealed glyphs are absolutely positioned (zero layout impact — the
    // "T", "L" and the rule are driven only by the fixed-font struts), so
    // their baseline is set here with --hl-dy. A zero-size inline-block with
    // vertical-align:baseline has no baseline of its own, so the spec drops
    // its *bottom* margin edge onto the surrounding line's baseline — its
    // rect gives the true baseline pixel, unlike an element's own rect
    // "bottom" (which is baseline + that font's descent, and differs between
    // the bold sans "T" and the reveal font, which is what was throwing the
    // alignment off).
    var baselineMarker = function () {
      var b = document.createElement("b");
      b.setAttribute("aria-hidden", "true");
      b.style.cssText = "display:inline-block;width:0;height:0;vertical-align:baseline;line-height:0;";
      return b;
    };
    var keepMarker = baselineMarker();
    mark.querySelector(".mark-word").appendChild(keepMarker);   // shares the T/L baseline
    var glyphEl = mark.querySelector(".hl > i");
    var glyphMarker = glyphEl ? baselineMarker() : null;
    if (glyphEl) glyphEl.appendChild(glyphMarker);

    // Each letter is its own element, so normal cross-letter kerning is
    // lost — measured live (via canvas, against whatever font is ACTUALLY
    // rendering right now) rather than hardcoded, so it's correct both for
    // the fallback font during the page-load font-swap and for Fraunces
    // once it's ready — a static value tuned for one would visibly "jump"
    // the moment the other took over.
    var kernFix = function (wordEl) {
      var keepEl = wordEl.querySelector(".keep");
      var firstHl = wordEl.querySelector(".hl");
      var strut = firstHl && firstHl.childNodes[0];
      if (!keepEl || !strut) return 0;
      var a = keepEl.textContent, b = strut.textContent;
      if (!a || !b) return 0;
      var cs = getComputedStyle(keepEl);
      kernCanvas.font = [cs.fontStyle, cs.fontWeight, cs.fontSize, cs.fontFamily].join(" ");
      var natural = kernCanvas.measureText(a + b).width;
      var summed = kernCanvas.measureText(a).width + kernCanvas.measureText(b).width;
      // canvas text doesn't apply CSS letter-spacing, but the live "T" box
      // does carry one trailing letter-spacing unit — cancel that out too,
      // or this over-corrects by exactly that amount.
      var tracking = parseFloat(cs.letterSpacing) || 0;
      return (natural - summed) - tracking;        // <=0: pull the letter back this much
    };

    var alignReveal = function () {
      if (!glyphMarker) return;
      mark.style.setProperty("--hl-dy", "0px");
      var d = keepMarker.getBoundingClientRect().top - glyphMarker.getBoundingClientRect().top;
      if (isFinite(d)) mark.style.setProperty("--hl-dy", d.toFixed(2) + "px");
      mark.querySelectorAll(".mark-word").forEach(function (w) {
        var firstHl = w.querySelector(".hl");
        if (firstHl) firstHl.style.marginLeft = kernFix(w).toFixed(2) + "px";
      });
    };
    alignReveal();
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(alignReveal);
    var alignT;
    window.addEventListener("resize", function () {
      clearTimeout(alignT);
      alignT = setTimeout(alignReveal, 150);
    }, { passive: true });

    if (!reduced) {
      var delay = mark.dataset.collapseDelay !== undefined ? parseInt(mark.dataset.collapseDelay, 10) : 2000;
      if (delay > 0) {
        window.setTimeout(function () { mark.classList.add("is-collapsed"); }, delay);
      } else {
        mark.classList.add("is-collapsed");   // e.g. the topbar's mini mark: starts shrunk, no flash
      }

      mark.addEventListener("click", function (e) {
        // first tap on a touch device reveals rather than navigates
        if (noHover && mark.classList.contains("is-collapsed") &&
            !mark.classList.contains("is-shown")) {
          e.preventDefault();
          mark.classList.add("is-shown");
        }
      });
      mark.addEventListener("focus", function () { mark.classList.add("is-shown"); });
      mark.addEventListener("blur", function () { mark.classList.remove("is-shown"); });
    }
  };
  document.querySelectorAll("[data-words]").forEach(buildMark);

  /* =====================================================================
     Top bar — hidden while the masthead is on screen, slides in once it
     has scrolled away. On pages with no masthead it stays visible.
     ===================================================================== */
  var bar = document.querySelector(".topbar");
  var masthead = document.querySelector(".masthead");
  if (bar && masthead) {
    var barShown = null, barTick = false;
    var syncBar = function () {
      barTick = false;
      var show = window.scrollY > masthead.offsetHeight - 8;
      if (show !== barShown) { barShown = show; bar.classList.toggle("show", show); }
    };
    syncBar();
    window.addEventListener("scroll", function () {
      if (!barTick) { barTick = true; requestAnimationFrame(syncBar); }
    }, { passive: true });
  } else if (bar) {
    bar.classList.add("show");
  }

  /* =====================================================================
     Reveal on scroll.
     ===================================================================== */
  var targets = document.querySelectorAll(".reveal");
  if (targets.length) {
    if (reduced || !("IntersectionObserver" in window)) {
      targets.forEach(function (t) { t.classList.add("in"); });
    } else {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) {
          if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); }
        });
      }, { rootMargin: "0px 0px -8% 0px", threshold: 0.06 });
      targets.forEach(function (t) { io.observe(t); });
    }
  }

  /* =====================================================================
     Work rows — two flush images. The panel under the cursor gets .is-active
     and its row .hovering; the split then animates through a single matched
     flex-grow transition (seamless across the seam). The active panel also
     flicks through its 3 frames. Pointer-only, so touch just taps links.
     ===================================================================== */
  if (!reduced && !window.matchMedia("(hover: none)").matches) {
    document.querySelectorAll(".proj-row").forEach(function (row) {
      var panels = [].slice.call(row.querySelectorAll(".proj"));
      if (panels.length < 2) return;

      var lane = panels.map(function (panel) {
        var frames = (panel.dataset.frames || "").split(",")
          .map(function (s) { return s.trim(); }).filter(Boolean);
        // preload + decode so the frame swap never blocks the main thread
        frames.forEach(function (src) {
          var im = new Image(); im.src = src;
          if (im.decode) im.decode().catch(function () {});
        });
        return {
          panel: panel,
          img: panel.querySelector(".proj-media img"),
          base: (panel.querySelector(".proj-media img") || {}).src,
          video: panel.querySelector(".proj-video"),
          frames: frames, timer: null, k: 0
        };
      });
      var active = -1;

      var setActive = function (i) {
        if (i === active) return;
        if (active > -1) {
          var prev = lane[active];
          prev.panel.classList.remove("is-active");
          if (prev.timer) { clearInterval(prev.timer); prev.timer = null; }
          if (prev.img) prev.img.src = prev.base;
          if (prev.video) { prev.video.pause(); prev.video.currentTime = 0; }
        }
        active = i;
        if (i > -1) {
          row.classList.add("hovering");
          var cur = lane[i];
          cur.panel.classList.add("is-active");
          if (cur.video) {
            cur.video.currentTime = 0;
            cur.video.play().catch(function () {});
          }
          if (cur.img && cur.frames.length > 1) {
            cur.k = 0;
            cur.timer = setInterval(function () {
              cur.k = (cur.k + 1) % cur.frames.length;
              cur.img.src = cur.frames[cur.k];
            }, 300);
          }
        } else {
          row.classList.remove("hovering");
        }
      };

      row.addEventListener("pointermove", function (e) {
        var p = e.target.closest(".proj");
        setActive(p ? panels.indexOf(p) : -1);
      }, { passive: true });
      row.addEventListener("pointerleave", function () { setActive(-1); });
      // keep keyboard users covered
      panels.forEach(function (p, i) {
        p.addEventListener("focusin", function () { setActive(i); });
        p.addEventListener("focusout", function () { setActive(-1); });
      });
    });
  }

  /* =====================================================================
     Custom cursor — a circular outline that follows the pointer in place
     of the system arrow (hidden via CSS on fine-pointer devices only).
     Position is set directly with no transition so it tracks instantly;
     only .is-active (shown once the pointer actually moves, so it doesn't
     appear stuck at 0,0 before the first move) ever gets a transition.
     ===================================================================== */
  if (!reduced && !noHover && window.matchMedia("(pointer: fine)").matches) {
    var cursorDot = document.createElement("div");
    cursorDot.id = "cursor-dot";
    cursorDot.setAttribute("aria-hidden", "true");
    document.body.appendChild(cursorDot);

    window.addEventListener("pointermove", function (e) {
      if (e.pointerType && e.pointerType !== "mouse") return;
      cursorDot.classList.add("is-active");
      cursorDot.style.transform =
        "translate(" + e.clientX + "px," + e.clientY + "px) translate(-50%,-50%)";
    }, { passive: true });
    document.addEventListener("mouseleave", function () {
      cursorDot.classList.remove("is-active");
    });
  }
})();
