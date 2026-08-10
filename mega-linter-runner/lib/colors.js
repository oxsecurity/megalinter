// Minimal replacement of the chalk dependency, based on node:util styleText
import { styleText } from "util";

const style = (format) => (text) => styleText(format, String(text));

export default {
  red: style("red"),
  green: style("green"),
  yellow: style("yellow"),
  cyan: style("cyan"),
  grey: style("grey"),
  bold: style("bold"),
  blueBright: style("blueBright"),
  whiteBright: style("whiteBright"),
  bgGray: style("bgGray"),
};
