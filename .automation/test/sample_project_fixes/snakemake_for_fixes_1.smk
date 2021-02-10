from snakemake.utils import min_version
min_version("5.14.0")
SAMPLES = ['s1', 's2'] # strings are normalised
CONDITIONS = ["a", "b", "longlonglonglonglonglonglonglonglonglonglonglonglonglonglonglong"] # long lines are wrapped
include: "rules/foo.smk" # 2 newlines

rule all:
    input: "data/results.txt" # newlines after keywords enforced and trailing comma

rule gets_separated_by_two_newlines:
    input:
        files = expand("long/string/to/data/files/gets_broken_by_black/{sample}.{condition}",sample=SAMPLES, condition=CONDITIONS)
if True:
    rule can_be_inside_python_code:
        input: "parameters", "get_indented"
        threads: 4 # Numeric params stay unindented
        params: key_val = "PEP8_formatted"
        run:

                print("weirdly_spaced_string_gets_respaced")
