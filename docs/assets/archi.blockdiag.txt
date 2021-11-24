blockdiag {
  code_change -> run_linters -> run_reporters;
  run_reporters -> code_change;
  code_change -> languages;
  code_change -> formatters
  code_change -> tooling_linters;
  run_linters -> console;
  run_linters -> text;
  run_linters -> json;
  run_linters -> ide_config;
  run_linters -> email;
  run_linters -> file_io;
  run_linters -> gh_pr;
  run_linters -> gh_status;
  run_linters -> tap;
  run_linters -> updated_sources;

  code_change [label = "Code Change", color="lightblue"];
  run_linters [label = "Run linters", color="lightblue"];
  run_reporters [label = "Run reporters", color="lightblue"];
  languages [label = "${language} languages", color="yellow"];
  formatters [label = "${format} formatters", color="yellow"];
  tooling_linters [label = "${tooling_format} tooling linters", color="yellow"];
  console [label = "Console", color="greenyellow"];
  text [label = "Text", color="greenyellow"];
  json [label = "JSON", color="greenyellow"];
  ide_config [label = "IDE Configuration", color="greenyellow"];
  email [label = "Email", color="greenyellow"];
  file_io [label = "file.io", color="greenyellow"];
  gh_pr [label = "GitHub Pull Request", color="greenyellow"];
  gh_status [label = "GitHub Status", color="greenyellow"];
  tap [label = "TAP", color="greenyellow"];
  updated_sources [label = "Updated sources", color="greenyellow"];
}
