// Select the hub build: define JX1_HUB_B for hub B.
#pragma once
#ifdef JX1_HUB_B
#include "config_hub_b.h"
#else
#include "config_hub_a.h"
#endif
