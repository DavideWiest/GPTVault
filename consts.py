


MDFILE_DIR = "mdfiles"

template = """

# Definition:
{def}

# Reference:
{ref}

# Fields: 
{fields}

# Known Since:
{knownsince}

"""

CONCEPT_DIR = "concepts"
SYSTEM_ROLE = "You are the knowledge-base of everything."
MAX_TOKENS_BASE = 256
MAX_NAME_LEN = 40
templateKeys = ["title", "definition", "known_since", "child_concepts", "concept_fields"]

conceptStorage = {

}
    