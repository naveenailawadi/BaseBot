ADD_TEXT_TO_INPUT = """
  var elm = arguments[0], txt = arguments[1];
  elm.value += txt;
  elm.dispatchEvent(new Event('change'));
  """
