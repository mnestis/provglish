from entity_template import entity
from activity_template import activity, activity_start, activity_end, activity_duration
from agent_template import agent
from start_template import start
from end_template import end
from generation_template import generation
from usage_template import usage
from communication_template import communication
from delegation_template import delegation
from attribution_template import attribution
from association_template import association
from invalidation_template import invalidation
from old_templates import _ag_der_ent_by_act_template
from old_templates import _collection_enum_template
from old_templates import _der_ent_by_act_template
from verbed_generation_template import generation as verbed_generation
from verbed_generation_agent_template import generation as verbed_generation_agent
from verbed_generation_agent_from_template import generation as verbed_generation_agent_from

all_templates = [
    entity,
    activity, activity_start, activity_end, activity_duration,
    agent,
    start,
    end,
    generation,
    usage,
    communication,
    delegation,
    attribution,
    association,
    invalidation,
    _ag_der_ent_by_act_template,
    _collection_enum_template,
    _der_ent_by_act_template,
    verbed_generation,
    verbed_generation_agent,
    verbed_generation_agent_from,
]
