//source: https://github.com/mynameistechno/finderjs

/**
 * check if variable is an element
 * @param  {*} potential element
 * @return {Boolean} return true if is an element
 */
 function _isElement(element) {
    try {
      // eslint-disable-next-line no-undef
      return element instanceof Element;
    } catch (error) {
      return !!(element && element.nodeType === 1);
    }
  }
  
  /**
   * createElement shortcut
   * @param  {String} tag
   * @return {Element} element
   */
  function _el(element) {
    var classes = [];
    var tag = element;
    var el;
  
    if (_isElement(element)) {
      return element;
    }
  
    classes = element.split('.');
    if (classes.length > 1) {
      tag = classes[0];
    }
    el = document.createElement(tag);
    _addClass(el, classes.slice(1));
  
    return el;
  }
  
  /**
   * createDocumentFragment shortcut
   * @return {DocumentFragment}
   */
  function __frag() {
    return document.createDocumentFragment();
  }
  
  /**
   * createTextNode shortcut
   * @return {TextNode}
   */
  function _text(text) {
    return document.createTextNode(text);
  }
  
  /**
   * remove element
   * @param  {Element} element to remove
   * @return {Element} removed element
   */
  function _remove(element) {
    if ('remove' in element) {
      element.remove();
    } else {
      element.parentNode.removeChild(element);
    }
  
    return element;
  }
  
  /**
   * Find first element that tests true, starting with the element itself
   * and traversing up through its ancestors
   * @param  {Element} element
   * @param  {Function} test fn - return true when element located
   * @return {Element}
   */
  function _closest(element, test) {
    var el = element;
  
    while (el) {
      if (test(el)) {
        return el;
      }
      el = el.parentNode;
    }
  
    return null;
  }
  
  /**
   * Add one or more classnames to an element
   * @param {Element} element
   * @param {Array.<string>|String} array of classnames or string with
   * classnames separated by whitespace
   * @return {Element}
   */
  function _addClass(element, className) {
    var classNames = className;
  
    function __addClass(el, cn) {
      if (!el.className) {
        el.className = cn;
      } else if (!_hasClass(el, cn)) {
        if (el.classList) {
          el.classList.add(cn);
        } else {
          el.className += ' ' + cn;
        }
      }
    }
  
    if (!Array.isArray(className)) {
      classNames = className.trim().split(/\s+/);
    }
    classNames.forEach(__addClass.bind(null, element));
  
    return element;
  }
  
  /**
   * Remove a class from an element
   * @param  {Element} element
   * @param  {Array.<string>|String} array of classnames or string with
   * @return {Element}
   */
  function _removeClass(element, className) {
    var classNames = className;
  
    function __removeClass(el, cn) {
      var classRegex;
      if (el.classList) {
        el.classList.remove(cn);
      } else {
        classRegex = new RegExp('(?:^|\\s)' + cn + '(?!\\S)', 'g');
        el.className = el.className.replace(classRegex, '').trim();
      }
    }
  
    if (!Array.isArray(className)) {
      classNames = className.trim().split(/\s+/);
    }
    classNames.forEach(__removeClass.bind(null, element));
  
    return element;
  }
  
  /**
   * Check if element has a class
   * @param  {Element}  element
   * @param  {String}  className
   * @return {boolean}
   */
  function _hasClass(element, className) {
    if (!element || !('className' in element)) {
      return false;
    }
  
    return element.className.split(/\s+/).indexOf(className) !== -1;
  }
  
  /**
   * Return all next siblings
   * @param  {Element} element
   * @return {Array.<element>}
   */
  function _nextSiblings(element) {
    var next = element.nextSibling;
    var siblings = [];
  
    while (next) {
      siblings.push(next);
      next = next.nextSibling;
    }
  
    return siblings;
  }
  
  /**
   * Return all prev siblings
   * @param  {Element} element
   * @return {Array.<element>}
   */
  function _previousSiblings(element) {
    var prev = element.previousSibling;
    var siblings = [];
  
    while (prev) {
      siblings.push(prev);
      prev = prev.previousSibling;
    }
  
    return siblings;
  }
  
  /**
   * Stop event propagation
   * @param  {Event} event
   * @return {Event}
   */
  function _stop(event) {
    event.stopPropagation();
    event.preventDefault();
  
    return event;
  }
  
  /**
   * Returns first element in parent that matches selector
   * @param  {Element} parent
   * @param  {String} selector
   * @return {Element | null}
   */
  function _first(parent, selector) {
    return parent.querySelector(selector);
  }
  
  function _append(parent, _children) {
    var _frag = __frag();
    var children = Array.isArray(_children) ? _children : [_children];
  
    children.forEach(_frag.appendChild.bind(_frag));
    parent.appendChild(_frag);
  
    return parent;
  }
  