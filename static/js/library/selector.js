class lite {
  constructor(e) {
    if( (e instanceof HTMLCollection) || (e instanceof NodeList) ) {
      this.elements = e;
    }
    else {
      this.elements = [e];
    }
  }
  getFirst() {
    return this.elements[0];
  }

  //DOM
  html(value = null) {
    if(value !== null) {
      this.getFirst().innerHTML = value;
      return this;
    }
    else
      return this.getFirst().innerHTML;
  }
  text(value = null) {
    if(value !== null) {
      this.getFirst().textContent = value;
      return this;
    }
    else
      return this.getFirst().textContent;
  }
  append(content) {
    this.getFirst().innerHTML += content;
  }
  prev() {
    return new lite(this.getFirst().previousElementSibling);
  }
  next() {
    return new lite(this.getFirst().nextElementSibling);
  }
  remove() {
    this.getFirst().parentNode.removeChild(this.getFirst());
    return this;
  }
  empty() {
    [...this.elements].forEach((e) => e.innerHTML = "");
    return this;
  }
  at(i) {
    return new lite(this.elements[i]);
  }

  //Selector Extenders
  find(q) {
    let e = this.getFirst().querySelectorAll(q);
    return new lite(e);
  }
  parent() {
    let e = this.getFirst().parentNode;
    return new lite(e);
  }
  closest(q) {
    let e = this.getFirst().closest(q);
    return new lite(e);
  }

  //Classes
  addClass(c) {
    if(c instanceof Array) {
      [...c].forEach((cl) => {
        [...this.elements].forEach((e) => e.classList.add(cl));
      });
    }

    [...this.elements].forEach((e) => e.classList.add(c));
    return this;
  }
  removeClass(c) {
    if(c instanceof Array) {
      [...c].forEach((cl) => {
        [...this.elements].forEach((e) => e.classList.remove(cl));
      });
    }
    [...this.elements].forEach((e) => e.classList.remove(c));
    return this;
  }
  toggleClass(c) {
    if(c instanceof Array) {
      [...c].forEach((cl) => {
        [...this.elements].forEach((e) => e.classList.toggle(cl));
      });
    }
    [...this.elements].forEach((e) => e.classList.toggle(c));
    return this;
  }
  hasClass(c) {
    return this.getFirst().classList.contains(c);
  }

  // CSS
  css(property, value = null) {
    if(property instanceof Object) {
      for(let key in property) {
        [...this.elements].forEach(function(e) {
          e.style[key] = property[key];
        });
      }
      return this;
    }
    else if(value !== null) {
      [...this.elements].forEach(function(e) {
        e.style[property] = value;
      });
      return this;
    }
    else {
      return this.getFirst().style[property];
    }
  }
  hide() {
    this.css("display", "none");
    return this;
  }
  show() {
    this.css("display", "");
    return this;
  }

  //Attributes
  attr(property, value = null) {
    if(value !== null) {
      [...this.elements].forEach(function(e) {
        e.setAttribute(property, value);
      });
      return this;
    }
    else
      return this.getFirst().getAttribute(property);
  }
  removeAttr(property) {
      [...this.elements].forEach(function(e) {
        e.removeAttribute(property);
      });
      return this;
  }
  data(property, value = null) {
    if(value !== null) {
      [...this.elements].forEach(function(e) {
        e.dataset[property] = value;
      });
      return this;
    }
    else
      return this.getFirst().dataset[property];
  }
  val(value = null) {
    if(value !== null) {
      [...this.elements].forEach((e) => e.value = value);
      return this;
    }
    else {
      return this.getFirst().value;
    }
  }
  size() {
    return this.elements.length;
  }

  //Event Listeners
  on(event, func) {
    [...this.elements].forEach((e) => e.addEventListener(event, func));
  }
  click(func) {
    this.on("click", func);
  }
  focus(func) {
    this.on("focus", func);
  }

  hover(func_in, func_out) {
    this.on("mouseenter", func_in);
    this.on("mouseleave", func_out);
  }

  in_and_out(func_in, func_out) {
    this.on("focus", func_in);
    this.on("blur", func_out);
  }

  //Extract Element(s)
  extract() {
    return this.elements;
  }

  //Loop
  forEach(func) {
    for(let e of this.elements) {
      func(e);
    }
  }

  //Effects
  fadeOut(ms = 500) {
    [...this.elements].forEach(function(elem) {
        if( ms ) {
          var opacity = 1;
          var timer = setInterval( function() {
            opacity -= 50 / ms;
            if( opacity <= 0 )
            {
              clearInterval(timer);
              opacity = 0;
              elem.style.display = "none";
              elem.style.visibility = "hidden";
            }
            elem.style.opacity = opacity;
            elem.style.filter = "alpha(opacity=" + opacity * 100 + ")";
          }, 50 );
        }
        else {
          elem.style.opacity = 0;
          elem.style.filter = "alpha(opacity=0)";
          elem.style.display = "none";
          elem.style.visibility = "hidden";
        }
    });
  }

  // Native fadeIn
  fadeIn(ms = 500) {
    [...this.elements].forEach(function(elem) {
      elem.style.opacity = 0;
      elem.style.filter = "alpha(opacity=0)";
      elem.style.display = "inline-block";
      elem.style.visibility = "visible";

      if( ms ) {
        var opacity = 0;
        var timer = setInterval( function() {
          opacity += 50 / ms;
          if( opacity >= 1 )
          {
            clearInterval(timer);
            opacity = 1;
          }
          elem.style.opacity = opacity;
          elem.style.filter = "alpha(opacity=" + opacity * 100 + ")";
        }, 50 );
      } else
      {
        elem.style.opacity = 1;
        elem.style.filter = "alpha(opacity=1)";
      }
    });
  }

}

function s(q) {
  if( q instanceof Element) {
    return new lite(q);
  }
  const firstLetter = q.charAt(0);
  let e;
  if( (q.includes("[")) || (q.includes(",")) || (q.includes(":")) || (q.includes(" ")) || (q.includes("*")) ) {
    e = document.querySelectorAll(q);
  }
  else {
    switch(firstLetter) {
      case "#":
        e = document.getElementById(q.slice(1));
        break;
      case ".":
        e = document.getElementsByClassName(q.slice(1));
        break;
      default:
        e = document.querySelectorAll(q);
        break;
    }
  }
  return new lite(e);
}
