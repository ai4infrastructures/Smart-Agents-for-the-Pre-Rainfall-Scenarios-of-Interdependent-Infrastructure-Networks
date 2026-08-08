import pandas as pd
from langchain.agents import Tool, initialize_agent, AgentType
from langchain_openai import ChatOpenAI
import os
from langchain.prompts import PromptTemplate
from shapefile_network_converter import shapefile_network_converter
from network_generator_for_interdependent_critical_infrastructures import network_generator_for_interdependent_critical_infrastructures
from network_generator_for_resource_constrained_interdependent_critical_infrastructures import network_generator_for_resource_constrained_interdependent_critical_infrastructures
from real_time_rainfall_event_extractor import real_time_rainfall_event_extractor
from ten_year_rainfall_event_extractor import ten_year_rainfall_event_extractor
from fifty_year_rainfall_event_extractor import fifty_year_rainfall_event_extractor
from one_hundred_year_rainfall_event_extractor import one_hundred_year_rainfall_event_extractor
from failure_node_extractor_for_HECRAS_simulations_under_real_time_rainfall_event import failure_node_extractor_for_HECRAS_simulations as failure_node_extractor_for_HECRAS_simulations_under_real_time_rainfall_event
from failure_node_extractor_for_HECRAS_simulations_under_ten_year_rainfall_event import failure_node_extractor_for_HECRAS_simulations as failure_node_extractor_for_HECRAS_simulations_under_ten_year_rainfall_event
from failure_node_extractor_for_HECRAS_simulations_under_fifty_year_rainfall_event import failure_node_extractor_for_HECRAS_simulations as failure_node_extractor_for_HECRAS_simulations_under_fifty_year_rainfall_event
from failure_node_extractor_for_HECRAS_simulations_under_one_hundred_year_rainfall_event import failure_node_extractor_for_HECRAS_simulations as failure_node_extractor_for_HECRAS_simulations_under_one_hundred_year_rainfall_event
from cascade_failure_simulator_based_on_Load_Capacity_model_with_uniform_load_redistribution import cascade_failure_simulator_based_on_Load_Capacity_model_with_uniform_load_redistribution
from cascade_failure_simulator_based_on_Load_Capacity_model_with_proportional_load_redistribution import cascade_failure_simulator_based_on_Load_Capacity_model_with_proportional_load_redistribution
from cascade_failure_simulator_based_on_Load_Capacity_model_with_nearest_neighbour_load_redistribution import cascade_failure_simulator_based_on_Load_Capacity_model_with_nearest_neighbour_load_redistribution
from cascade_failure_simulator_based_on_Monte_Carlo_model import cascade_failure_simulator_based_on_Monte_Carlo_model
from cascade_failure_simulator_based_on_Motter_Lai_model import cascade_failure_simulator_based_on_Motter_Lai_model
from post_disaster_assessment_based_on_average_path_length import post_disaster_assessment_based_on_average_path_length
from post_disaster_assessment_based_on_connectivity import post_disaster_assessment_based_on_connectivity
from post_disaster_assessment_based_on_diameter import post_disaster_assessment_based_on_diameter
from post_disaster_assessment_based_on_global_network_efficiency import post_disaster_assessment_based_on_global_network_efficiency
from post_disaster_assessment_based_on_node_accessibility import post_disaster_assessment_based_on_node_accessibility
from during_recovery_assessment_of_betweenness_based_recovery_order import during_recovery_assessment_of_betweenness_based_recovery_order
from during_recovery_assessment_of_node_degree_based_recovery_order import during_recovery_assessment_of_node_degree_based_recovery_order
from during_recovery_assessment_of_propagation_ranges_based_recovery_order import during_recovery_assessment_of_propagation_ranges_based_recovery_order
from during_recovery_assessment_of_GA_derived_GSCC_based_recovery_order import during_recovery_assessment_of_GA_derived_GSCC_based_recovery_order
from during_recovery_assessment_of_SA_derived_GSCC_based_recovery_order import during_recovery_assessment_of_SA_derived_GSCC_based_recovery_order
from during_recovery_assessment_of_GA_derived_population_based_recovery_order import during_recovery_assessment_of_GA_derived_population_based_recovery_order
from during_recovery_assessment_of_SA_derived_population_based_recovery_order import during_recovery_assessment_of_SA_derived_population_based_recovery_order
from recovery_order_determined_based_on_betweenness import recovery_order_determined_based_on_betweenness
from recovery_order_determined_based_on_node_degree import recovery_order_determined_based_on_node_degree
from recovery_order_determined_based_on_propagation_ranges import recovery_order_determined_based_on_propagation_ranges
from recovery_order_determined_based_on_GSCC_by_GA import recovery_order_determined_based_on_GSCC_by_GA
from recovery_order_determined_based_on_GSCC_by_SA import recovery_order_determined_based_on_GSCC_by_SA
from recovery_order_determined_based_on_population_by_GA import recovery_order_determined_based_on_population_by_GA
from recovery_order_determined_based_on_population_by_SA import recovery_order_determined_based_on_population_by_SA
from recovery_plan_determined_based_on_WCC_by_GA import recovery_plan_determined_based_on_WCC_by_GA
from recovery_plan_determined_based_on_population_by_GA import recovery_plan_determined_based_on_population_by_GA
from recovery_plan_determined_based_on_clustering_coefficient import recovery_plan_determined_based_on_clustering_coefficient
from recovery_plan_determined_under_resource_constraints import recovery_plan_determined_under_resource_constraints
from recovery_plan_determined_under_cost_constraints import recovery_plan_determined_under_cost_constraints
from langchain.callbacks.base import BaseCallbackHandler


class ProcessLogger(BaseCallbackHandler):
    def __init__(self):
        self.logs = []

    def reset(self):
        self.logs = []

    def on_llm_start(self, serialized, prompts, **kwargs):
        pass  # 不记录 LLM 开始执行

    def on_llm_end(self, response, **kwargs):
        pass  # 不记录 LLM 执行结束

    def on_chain_start(self, serialized, inputs, **kwargs):
        pass  # 不记录 chain 开始

    def on_chain_end(self, outputs, **kwargs):
        pass  # 不记录 chain 结束

    def on_agent_action(self, action, **kwargs):
        self.logs.append(f"Action: {action.tool}")

    def on_agent_finish(self, finish, **kwargs):
        pass  # 不记录


# 创建自定义回调处理器实例
process_logger = ProcessLogger()

# Set OpenAI API key
os.environ["OPENAI_API_KEY"] = ""
llm = ChatOpenAI(
    openai_api_key=os.environ["OPENAI_API_KEY"],
    temperature=0,
    model_name='gpt-5'
)

# Create tool instances
shapefile_network_converter_tool = Tool.from_function(
    name="shapefile_network_converter",
    func=shapefile_network_converter,
    description="This tool is to convert shapefile network. It reads the shapefile information in infrastructures_information.json from Global_Data.json as input. It outputs the infrastructure networks in infrastructures_networks.json and saved in Global_Data.json. If this function is running, you could find the path of infrastructures_networks.json in Global_Data.json."
)

network_generator_for_interdependent_critical_infrastructures_tool = Tool.from_function(
    name="network_generator_for_interdependent_critical_infrastructures",
    func=network_generator_for_interdependent_critical_infrastructures,
    description="This tool is to generate network for interdependent critical infrastructures. It reads the infrastructure networks in infrastructures_networks.json from Global_Data.json as input. It outputs the interdependent critical infrastructures networks in interdependent_critical_infrastructures_networks.json and saved in Global_Data.json. If this function is running, you could find the path of interdependent_critical_infrastructures_networks.json in Global_Data.json."
)

network_generator_for_resource_constrained_interdependent_critical_infrastructures_tool = Tool.from_function(
    name="network_generator_for_resource_constrained_interdependent_critical_infrastructures",
    func=network_generator_for_resource_constrained_interdependent_critical_infrastructures,
    description="This tool is to generate network for resource-constrained interdependent critical infrastructures. It reads the infrastructure networks in infrastructures_networks.json from Global_Data.json as input. It outputs the resource constrained interdependent critical infrastructures networks in resource_constrained_interdependent_critical_infrastructures_networks.json and saved in Global_Data.json. If this function is running, you could find the path of resource_constrained_interdependent_critical_infrastructures_networks.json in Global_Data.json."
)

real_time_rainfall_event_extractor_tool = Tool.from_function(
    name="real_time_rainfall_event_extractor",
    func=real_time_rainfall_event_extractor,
    description="This tool is to extract real-time rainfall event. It outputs the real-time rainfall event data in real_time_rainfall_event.json and saved in Global_Data.json. If this function is running, you could find the path of real_time_rainfall_event.json in Global_Data.json."
)

ten_year_rainfall_event_extractor_tool = Tool.from_function(
    name="ten_year_rainfall_event_extractor",
    func=ten_year_rainfall_event_extractor,
    description="This tool is to extract ten-year rainfall event. It outputs the ten-year rainfall event data in ten_year_rainfall_event.json and saved in Global_Data.json. If this function is running, you could find the path of ten_year_rainfall_event.json in Global_Data.json."
)

fifty_year_rainfall_event_extractor_tool = Tool.from_function(
    name="fifty_year_rainfall_event_extractor",
    func=fifty_year_rainfall_event_extractor,
    description="This tool is to extract fifty-year rainfall event. It outputs the fifty-year rainfall event data in fifty_year_rainfall_event.json and saved in Global_Data.json. If this function is running, you could find the path of fifty_year_rainfall_event.json in Global_Data.json."
)

one_hundred_year_rainfall_event_extractor_tool = Tool.from_function(
    name="one_hundred_year_rainfall_event_extractor",
    func=one_hundred_year_rainfall_event_extractor,
    description="This tool is to extract one-hundred-year rainfall event. It outputs the one-hundred-year rainfall event data in one_hundred_year_rainfall_event.json and saved in Global_Data.json. If this function is running, you could find the path of one_hundred_year_rainfall_event.json in Global_Data.json."
)

failure_node_extractor_for_HECRAS_simulations_under_real_time_rainfall_event_tool = Tool.from_function(
    name="failure_node_extractor_for_HECRAS_simulations_under_real_time_rainfall_event",
    func=failure_node_extractor_for_HECRAS_simulations_under_real_time_rainfall_event,
    description="This tool is to extract failure node for HEC-RAS simulations under real-time rainfall event. It reads the real-time rainfall event data in real_time_rainfall_event.json from Global_Data.json as input. It outputs the failure node in failure_node_after_HECRAS_simulations.json and saved in Global_Data.json. If this function is running, you could find the path of failure_node_after_HECRAS_simulations.json in Global_Data.json."
)

failure_node_extractor_for_HECRAS_simulations_under_ten_year_rainfall_event_tool = Tool.from_function(
    name="failure_node_extractor_for_HECRAS_simulations_under_ten_year_rainfall_event",
    func=failure_node_extractor_for_HECRAS_simulations_under_ten_year_rainfall_event,
    description="This tool is to extract failure node for HEC-RAS simulations under ten-year rainfall event. It reads the ten-year rainfall event data in ten_year_rainfall_event.json from Global_Data.json as input. It outputs the failure node in failure_node_after_HECRAS_simulations.json and saved in Global_Data.json. If this function is running, you could find the path of failure_node_after_HECRAS_simulations.json in Global_Data.json."
)

failure_node_extractor_for_HECRAS_simulations_under_fifty_year_rainfall_event_tool = Tool.from_function(
    name="failure_node_extractor_for_HECRAS_simulations_under_fifty_year_rainfall_event",
    func=failure_node_extractor_for_HECRAS_simulations_under_fifty_year_rainfall_event,
    description="This tool is to extract failure node for HEC-RAS simulations under fifty-year rainfall event. It reads the fifty-year rainfall event data in fifty_year_rainfall_event.json from Global_Data.json as input. It outputs the failure node in failure_node_after_HECRAS_simulations.json and saved in Global_Data.json. If this function is running, you could find the path of failure_node_after_HECRAS_simulations.json in Global_Data.json."
)

failure_node_extractor_for_HECRAS_simulations_under_one_hundred_year_rainfall_event_tool = Tool.from_function(
    name="failure_node_extractor_for_HECRAS_simulations_under_one_hundred_year_rainfall_event",
    func=failure_node_extractor_for_HECRAS_simulations_under_one_hundred_year_rainfall_event,
    description="This tool is to extract failure node for HEC-RAS simulations under one-hundred-year rainfall event. It reads the one-hundred-year rainfall event data in one_hundred_year_rainfall_event.json from Global_Data.json as input. It outputs the failure node in failure_node_after_HECRAS_simulations.json and saved in Global_Data.json. If this function is running, you could find the path of failure_node_after_HECRAS_simulations.json in Global_Data.json."
)

cascade_failure_simulator_based_on_Load_Capacity_model_with_uniform_load_redistribution_tool = Tool.from_function(
    name="cascade_failure_simulator_based_on_Load_Capacity_model_with_uniform_load_redistribution",
    func=cascade_failure_simulator_based_on_Load_Capacity_model_with_uniform_load_redistribution,
    description="This tool is to simulate cascade failure based on Load-Capacity model with uniform load redistribution. It reads the interdependent critical infrastructures networks in interdependent_critical_infrastructures_networks.json, the failure node in failure_node_after_HECRAS_simulations.json, and the load distribution in load_distribution.json from Global_Data.json as input. It outputs the cascade failure simulator in cascade_failure_simulator_based_on_Load_Capacity_model_with_uniform_load_redistribution.json and saved in Global_Data.json. If this function is running, you could find the path of cascade_failure_simulator_based_on_Load_Capacity_model_with_uniform_load_redistribution.json in Global_Data.json."
)

cascade_failure_simulator_based_on_Load_Capacity_model_with_proportional_load_redistribution_tool = Tool.from_function(
    name="cascade_failure_simulator_based_on_Load_Capacity_model_with_proportional_load_redistribution",
    func=cascade_failure_simulator_based_on_Load_Capacity_model_with_proportional_load_redistribution,
    description="This tool is to simulate cascade failure based on Load-Capacity model with proportional load redistribution. It reads the interdependent critical infrastructures networks in interdependent_critical_infrastructures_networks.json, the failure node in failure_node_after_HECRAS_simulations.json, and the load distribution in load_distribution.json from Global_Data.json as input. It outputs the cascade failure simulator in cascade_failure_simulator_based_on_Load_Capacity_model_with_proportional_load_redistribution.json and saved in Global_Data.json. If this function is running, you could find the path of cascade_failure_simulator_based_on_Load_Capacity_model_with_proportional_load_redistribution.json in Global_Data.json."
)

cascade_failure_simulator_based_on_Load_Capacity_model_with_nearest_neighbour_load_redistribution_tool = Tool.from_function(
    name="cascade_failure_simulator_based_on_Load_Capacity_model_with_nearest_neighbour_load_redistribution",
    func=cascade_failure_simulator_based_on_Load_Capacity_model_with_nearest_neighbour_load_redistribution,
    description="This tool is to simulate cascade failure based on Load-Capacity model with nearest neighbour load redistribution. It reads the interdependent critical infrastructures networks in interdependent_critical_infrastructures_networks.json, the failure node in failure_node_after_HECRAS_simulations.json, and the load distribution in load_distribution.json from Global_Data.json as input. It outputs the cascade failure simulator in cascade_failure_simulator_based_on_Load_Capacity_model_with_nearest_neighbour_load_redistribution.json and saved in Global_Data.json. If this function is running, you could find the path of cascade_failure_simulator_based_on_Load_Capacity_model_with_nearest_neighbour_load_redistribution.json in Global_Data.json."
)

cascade_failure_simulator_based_on_Monte_Carlo_model_tool = Tool.from_function(
    name="cascade_failure_simulator_based_on_Monte_Carlo_model",
    func=cascade_failure_simulator_based_on_Monte_Carlo_model,
    description="This tool is to simulate cascade failure based on Monte Carlo model. It reads the interdependent critical infrastructures networks in interdependent_critical_infrastructures_networks.json and the failure node in failure_node_after_HECRAS_simulations.json from Global_Data.json as input. It outputs the cascade failure simulator in cascade_failure_simulator_based_on_Monte_Carlo_model.json and saved in Global_Data.json. If this function is running, you could find the path of cascade_failure_simulator_based_on_Monte_Carlo_model.json in Global_Data.json."
)

cascade_failure_simulator_based_on_Motter_Lai_model_tool = Tool.from_function(
    name="cascade_failure_simulator_based_on_Motter_Lai_model",
    func=cascade_failure_simulator_based_on_Motter_Lai_model,
    description="This tool is to simulate cascade failure based on Motter Lai model. It reads the interdependent critical infrastructures networks in interdependent_critical_infrastructures_networks.json and the failure node in failure_node_after_HECRAS_simulations.json from Global_Data.json as input. It outputs the cascade failure simulator in cascade_failure_simulator_based_on_Motter_Lai_model.json and saved in Global_Data.json. If this function is running, you could find the path of cascade_failure_simulator_based_on_Motter_Lai_model.json in Global_Data.json."
)

post_disaster_assessment_based_on_average_path_length_tool = Tool.from_function(
    name="post_disaster_assessment_based_on_average_path_length",
    func=post_disaster_assessment_based_on_average_path_length,
    description="This tool is to assess post-disaster assessment based on average path length. It reads the interdependent critical infrastructures networks in interdependent_critical_infrastructures_networks.json and the failure node in cascade_failure_simulator_based_on_Motter_Lai_model.json from Global_Data.json as input. It outputs the post-disaster assessment in post_disaster_assessment_based_on_average_path_length.json and saved in Global_Data.json. If this function is running, you could find the path of post_disaster_assessment_based_on_average_path_length.json in Global_Data.json."
)

post_disaster_assessment_based_on_connectivity_tool = Tool.from_function(
    name="post_disaster_assessment_based_on_connectivity",
    func=post_disaster_assessment_based_on_connectivity,
    description="This tool is to assess post-disaster assessment based on connectivity. It reads the interdependent critical infrastructures networks in interdependent_critical_infrastructures_networks.json and the failure node in cascade_failure_simulator_based_on_Motter_Lai_model.json from Global_Data.json as input. It outputs the post-disaster assessment in post_disaster_assessment_based_on_connectivity.json and saved in Global_Data.json. If this function is running, you could find the path of post_disaster_assessment_based_on_connectivity.json in Global_Data.json."
)

post_disaster_assessment_based_on_diameter_tool = Tool.from_function(
    name="post_disaster_assessment_based_on_diameter",
    func=post_disaster_assessment_based_on_diameter,
    description="This tool is to assess post-disaster assessment based on diameter. It reads the interdependent critical infrastructures networks in interdependent_critical_infrastructures_networks.json and the failure node in cascade_failure_simulator_based_on_Motter_Lai_model.json from Global_Data.json as input. It outputs the post-disaster assessment in post_disaster_assessment_based_on_diameter.json and saved in Global_Data.json. If this function is running, you could find the path of post_disaster_assessment_based_on_diameter.json in Global_Data.json."
)

post_disaster_assessment_based_on_global_network_efficiency_tool = Tool.from_function(
    name="post_disaster_assessment_based_on_global_network_efficiency",
    func=post_disaster_assessment_based_on_global_network_efficiency,
    description="This tool is to assess post-disaster assessment based on global network efficiency. It reads the interdependent critical infrastructures networks in interdependent_critical_infrastructures_networks.json and the failure node in cascade_failure_simulator_based_on_Motter_Lai_model.json from Global_Data.json as input. It outputs the post-disaster assessment in post_disaster_assessment_based_on_global_network_efficiency.json and saved in Global_Data.json. If this function is running, you could find the path of post_disaster_assessment_based_on_global_network_efficiency.json in Global_Data.json."
)

post_disaster_assessment_based_on_node_accessibility_tool = Tool.from_function(
    name="post_disaster_assessment_based_on_node_accessibility",
    func=post_disaster_assessment_based_on_node_accessibility,
    description="This tool is to assess post-disaster assessment based on node accessibility. It reads the interdependent critical infrastructures networks in interdependent_critical_infrastructures_networks.json and the failure node in cascade_failure_simulator_based_on_Motter_Lai_model.json from Global_Data.json as input. It outputs the post-disaster assessment in post_disaster_assessment_based_on_node_accessibility.json and saved in Global_Data.json. If this function is running, you could find the path of post_disaster_assessment_based_on_node_accessibility.json in Global_Data.json."
)

during_recovery_assessment_of_betweenness_based_recovery_order_tool = Tool.from_function(
    name="during_recovery_assessment_of_betweenness_based_recovery_order",
    func=during_recovery_assessment_of_betweenness_based_recovery_order,
    description="This tool is to assess recovery order based on betweenness during recovery. It reads the interdependent critical infrastructures networks in interdependent_critical_infrastructures_networks.json, the population data in population_data.json, and the recovery order in recovery_order_determined_based_on_betweenness.json from Global_Data.json as input. It outputs the recovery assessment of recovery order in during_recovery_assessment_of_betweenness_based_recovery_order.json and saved in Global_Data.json. If this function is running, you could find the path of during_recovery_assessment_of_betweenness_based_recovery_order.json in Global_Data.json."
)

during_recovery_assessment_of_node_degree_based_recovery_order_tool = Tool.from_function(
    name="during_recovery_assessment_of_node_degree_based_recovery_order",
    func=during_recovery_assessment_of_node_degree_based_recovery_order,
    description="This tool is to assess recovery order based on node degree during recovery. It reads the interdependent critical infrastructures networks in interdependent_critical_infrastructures_networks.json, the population data in population_data.json, and the recovery order in recovery_order_determined_based_on_node_degree.json from Global_Data.json as input. It outputs the recovery assessment of recovery order in during_recovery_assessment_of_node_degree_based_recovery_order.json. If this function is running, you could find the path of during_recovery_assessment_of_node_degree_based_recovery_order.json in Global_Data.json."
)

during_recovery_assessment_of_propagation_ranges_based_recovery_order_tool = Tool.from_function(
    name="during_recovery_assessment_of_propagation_ranges_based_recovery_order",
    func=during_recovery_assessment_of_propagation_ranges_based_recovery_order,
    description="This tool is to assess recovery order based on propagation ranges during recovery. It reads the interdependent critical infrastructures networks in interdependent_critical_infrastructures_networks.json, the population data in population_data.json, and the recovery order in recovery_order_determined_based_on_propagation_ranges.json from Global_Data.json as input. It outputs the recovery assessment of recovery order in during_recovery_assessment_of_propagation_ranges_based_recovery_order.json and saved in Global_Data.json. If this function is running, you could find the path of during_recovery_assessment_of_propagation_ranges_based_recovery_order.json in Global_Data.json."
)

during_recovery_assessment_of_GA_derived_GSCC_based_recovery_order_tool = Tool.from_function(
    name="during_recovery_assessment_of_GA_derived_GSCC_based_recovery_order",
    func=during_recovery_assessment_of_GA_derived_GSCC_based_recovery_order,
    description="This tool is to assess recovery order based on GSCC by GA during recovery. It reads the interdependent critical infrastructures networks in interdependent_critical_infrastructures_networks.json, the population data in population_data.json, and the recovery order in recovery_order_determined_based_on_GSCC_by_GA.json from Global_Data.json as input. It outputs the recovery assessment of recovery order in during_recovery_assessment_of_GA_derived_GSCC_based_recovery_order.json and saved in Global_Data.json. If this function is running, you could find the path of during_recovery_assessment_of_GA_derived_GSCC_based_recovery_order.json in Global_Data.json."
)

during_recovery_assessment_of_SA_derived_GSCC_based_recovery_order_tool = Tool.from_function(
    name="during_recovery_assessment_of_SA_derived_GSCC_based_recovery_order",
    func=during_recovery_assessment_of_SA_derived_GSCC_based_recovery_order,
    description="This tool is to assess recovery order based on GSCC by SA during recovery. It reads the interdependent critical infrastructures networks in interdependent_critical_infrastructures_networks.json, the population data in population_data.json, and the recovery order in recovery_order_determined_based_on_GSCC_by_SA.json from Global_Data.json as input. It outputs the recovery assessment of recovery order in during_recovery_assessment_of_SA_derived_GSCC_based_recovery_order.json and saved in Global_Data.json. If this function is running, you could find the path of during_recovery_assessment_of_SA_derived_GSCC_based_recovery_order.json in Global_Data.json."
)

during_recovery_assessment_of_GA_derived_population_based_recovery_order_tool = Tool.from_function(
    name="during_recovery_assessment_of_GA_derived_population_based_recovery_order",
    func=during_recovery_assessment_of_GA_derived_population_based_recovery_order,
    description="This tool is to assess recovery order based on population by GA during recovery. It reads the interdependent critical infrastructures networks in interdependent_critical_infrastructures_networks.json, the population data in population_data.json, and the recovery order in recovery_order_determined_based_on_population_by_GA.json from Global_Data.json as input. It outputs the recovery assessment of recovery order in during_recovery_assessment_of_GA_derived_population_based_recovery_order.json and saved in Global_Data.json. If this function is running, you could find the path of during_recovery_assessment_of_GA_derived_population_based_recovery_order.json in Global_Data.json."
)

during_recovery_assessment_of_SA_derived_population_based_recovery_order_tool = Tool.from_function(
    name="during_recovery_assessment_of_SA_derived_population_based_recovery_order",
    func=during_recovery_assessment_of_SA_derived_population_based_recovery_order,
    description="This tool is to assess recovery order based on population by SA during recovery. It reads the interdependent critical infrastructures networks in interdependent_critical_infrastructures_networks.json, the population data in population_data.json, and the recovery order in recovery_order_determined_based_on_population_by_SA.json from Global_Data.json as input. It outputs the recovery assessment of recovery order in during_recovery_assessment_of_SA_derived_population_based_recovery_order.json and saved in Global_Data.json. If this function is running, you could find the path of during_recovery_assessment_of_SA_derived_population_based_recovery_order.json in Global_Data.json."
)

recovery_order_determined_based_on_betweenness_tool = Tool.from_function(
    name="recovery_order_determined_based_on_betweenness",
    func=recovery_order_determined_based_on_betweenness,
    description="This tool is to determine recovery order based on betweenness. It reads the interdependent critical infrastructures networks in interdependent_critical_infrastructures_networks.json and the failure node in cascade_failure_simulator_based_on_Motter_Lai_model.json from Global_Data.json as input. It outputs the recovery order in recovery_order_determined_based_on_betweenness.json and saved in Global_Data.json. If this function is running, you could find the path of recovery_order_determined_based_on_betweenness.json in Global_Data.json."
)

recovery_order_determined_based_on_node_degree_tool = Tool.from_function(
    name="recovery_order_determined_based_on_node_degree",
    func=recovery_order_determined_based_on_node_degree,
    description="This tool is to determine recovery order based on node degree. It reads the interdependent critical infrastructures networks in interdependent_critical_infrastructures_networks.json and the failure node in cascade_failure_simulator_based_on_Motter_Lai_model.json from Global_Data.json as input. It outputs the recovery order in recovery_order_determined_based_on_node_degree.json and saved in Global_Data.json. If this function is running, you could find the path of recovery_order_determined_based_on_node_degree.json in Global_Data.json."
)

recovery_order_determined_based_on_propagation_ranges_tool = Tool.from_function(
    name="recovery_order_determined_based_on_propagation_ranges",
    func=recovery_order_determined_based_on_propagation_ranges,
    description="This tool is to determine recovery order based on propagation ranges. It reads the interdependent critical infrastructures networks in interdependent_critical_infrastructures_networks.json and the failure node in cascade_failure_simulator_based_on_Motter_Lai_model.json from Global_Data.json as input. It outputs the recovery order in recovery_order_determined_based_on_propagation_ranges.json and saved in Global_Data.json. If this function is running, you could find the path of recovery_order_determined_based_on_propagation_ranges.json in Global_Data.json."
)

recovery_order_determined_based_on_GSCC_by_GA_tool = Tool.from_function(
    name="recovery_order_determined_based_on_GSCC_by_GA",
    func=recovery_order_determined_based_on_GSCC_by_GA,
    description="This tool is to determine recovery order based on GSCC by GA. It reads the interdependent critical infrastructures networks in interdependent_critical_infrastructures_networks.json and the failure node in cascade_failure_simulator_based_on_Motter_Lai_model.json from Global_Data.json as input. It outputs the recovery order in recovery_order_determined_based_on_GSCC_by_GA.json and saved in Global_Data.json. If this function is running, you could find the path of recovery_order_determined_based_on_GSCC_by_GA.json in Global_Data.json."
)

recovery_order_determined_based_on_GSCC_by_SA_tool = Tool.from_function(
    name="recovery_order_determined_based_on_GSCC_by_SA",
    func=recovery_order_determined_based_on_GSCC_by_SA,
    description="This tool is to determine recovery order based on GSCC by SA. It reads the interdependent critical infrastructures networks in interdependent_critical_infrastructures_networks.json and the failure node in cascade_failure_simulator_based_on_Motter_Lai_model.json from Global_Data.json as input. It outputs the recovery order in recovery_order_determined_based_on_GSCC_by_SA.json and saved in Global_Data.json. If this function is running, you could find the path of recovery_order_determined_based_on_GSCC_by_SA.json in Global_Data.json."
)

recovery_order_determined_based_on_population_by_GA_tool = Tool.from_function(
    name="recovery_order_determined_based_on_population_by_GA",
    func=recovery_order_determined_based_on_population_by_GA,
    description="This tool is to determine recovery order based on population by GA. It reads the interdependent critical infrastructures networks in interdependent_critical_infrastructures_networks.json, the population data in population_data.json, and the failure node in cascade_failure_simulator_based_on_Motter_Lai_model.json from Global_Data.json as input. It outputs the recovery order in recovery_order_determined_based_on_population_by_GA.json and saved in Global_Data.json. If this function is running, you could find the path of recovery_order_determined_based_on_population_by_GA.json in Global_Data.json."
)

recovery_order_determined_based_on_population_by_SA_tool = Tool.from_function(
    name="recovery_order_determined_based_on_population_by_SA",
    func=recovery_order_determined_based_on_population_by_SA,
    description="This tool is to determine recovery order based on population by SA. It reads the interdependent critical infrastructures networks in interdependent_critical_infrastructures_networks.json, the population data in population_data.json, and the failure node in cascade_failure_simulator_based_on_Motter_Lai_model.json from Global_Data.json as input. It outputs the recovery order in recovery_order_determined_based_on_population_by_SA.json and saved in Global_Data.json. If this function is running, you could find the path of recovery_order_determined_based_on_population_by_SA.json in Global_Data.json."
)

recovery_plan_determined_based_on_WCC_by_GA_tool = Tool.from_function(
    name="recovery_plan_determined_based_on_WCC_by_GA",
    func=recovery_plan_determined_based_on_WCC_by_GA,
    description="This tool is to determine recovery plan based on WCC by GA. It reads the resource constrained interdependent critical infrastructures networks in resource_constrained_interdependent_critical_infrastructures_networks.json, the resource constraints per day in resource_constraints_per_day.json, the population data in population_data.json, and the failure node in cascade_failure_simulator_based_on_Motter_Lai_model.json from Global_Data.json as input. It outputs the recovery plan in recovery_plan_determined_based_on_WCC_by_GA.json and saved in Global_Data.json. If this function is running, you could find the path of recovery_plan_determined_based_on_WCC_by_GA.json in Global_Data.json."
)

recovery_plan_determined_based_on_population_by_GA_tool = Tool.from_function(
    name="recovery_plan_determined_based_on_population_by_GA",
    func=recovery_plan_determined_based_on_population_by_GA,
    description="This tool is to determine recovery plan based on population by GA. It reads the resource constrained interdependent critical infrastructures networks in resource_constrained_interdependent_critical_infrastructures_networks.json, the resource constraints per day in resource_constraints_per_day.json, the population data in population_data.json, and the failure node in cascade_failure_simulator_based_on_Motter_Lai_model.json from Global_Data.json as input. It outputs the recovery plan in recovery_plan_determined_based_on_population_by_GA.json and saved in Global_Data.json. If this function is running, you could find the path of recovery_plan_determined_based_on_population_by_GA.json in Global_Data.json."
)

recovery_plan_determined_based_on_clustering_coefficient_tool = Tool.from_function(
    name="recovery_plan_determined_based_on_clustering_coefficient",
    func=recovery_plan_determined_based_on_clustering_coefficient,
    description="This tool is to determine recovery plan based on clustering coefficient. It reads the resource constrained interdependent critical infrastructures networks in resource_constrained_interdependent_critical_infrastructures_networks.json, the resource constraints per day in resource_constraints_per_day.json, and the failure node in cascade_failure_simulator_based_on_Motter_Lai_model.json from Global_Data.json as input. It outputs the recovery plan in recovery_plan_determined_based_on_clustering_coefficient.json and saved in Global_Data.json. If this function is running, you could find the path of recovery_plan_determined_based_on_clustering_coefficient.json in Global_Data.json."
)

recovery_plan_determined_under_resource_constraints_tool = Tool.from_function(
    name="recovery_plan_determined_under_resource_constraints",
    func=recovery_plan_determined_under_resource_constraints,
    description="This tool is to determine recovery plan under resource constraints. It reads the resource constrained interdependent critical infrastructures networks in resource_constrained_interdependent_critical_infrastructures_networks.json, the population data in population_data.json, and the failure node in cascade_failure_simulator_based_on_Motter_Lai_model.json from Global_Data.json as input. It outputs the recovery plan in recovery_plan_determined_under_resource_constraints.json and saved in Global_Data.json. If this function is running, you could find the path of recovery_plan_determined_under_resource_constraints.json in Global_Data.json."
)

recovery_plan_determined_under_cost_constraints_tool = Tool.from_function(
    name="recovery_plan_determined_under_cost_constraints",
    func=recovery_plan_determined_under_cost_constraints,
    description="This tool is to determine recovery plan under cost constraints. It reads the resource constrained interdependent critical infrastructures networks in resource_constrained_interdependent_critical_infrastructures_networks.json, the population data in population_data.json, and the failure node in cascade_failure_simulator_based_on_Motter_Lai_model.json from Global_Data.json as input. It outputs the recovery plan in recovery_plan_determined_under_cost_constraints.json and saved in Global_Data.json. If this function is running, you could find the path of recovery_plan_determined_under_cost_constraints.json in Global_Data.json."
)


tools = [
    shapefile_network_converter_tool,
    network_generator_for_interdependent_critical_infrastructures_tool,
    network_generator_for_resource_constrained_interdependent_critical_infrastructures_tool,
    real_time_rainfall_event_extractor_tool,
    ten_year_rainfall_event_extractor_tool,
    fifty_year_rainfall_event_extractor_tool,
    one_hundred_year_rainfall_event_extractor_tool,
    failure_node_extractor_for_HECRAS_simulations_under_real_time_rainfall_event_tool,
    failure_node_extractor_for_HECRAS_simulations_under_ten_year_rainfall_event_tool,
    failure_node_extractor_for_HECRAS_simulations_under_fifty_year_rainfall_event_tool,
    failure_node_extractor_for_HECRAS_simulations_under_one_hundred_year_rainfall_event_tool,
    cascade_failure_simulator_based_on_Load_Capacity_model_with_uniform_load_redistribution_tool,
    cascade_failure_simulator_based_on_Load_Capacity_model_with_proportional_load_redistribution_tool,
    cascade_failure_simulator_based_on_Load_Capacity_model_with_nearest_neighbour_load_redistribution_tool,
    cascade_failure_simulator_based_on_Monte_Carlo_model_tool,
    cascade_failure_simulator_based_on_Motter_Lai_model_tool,
    post_disaster_assessment_based_on_average_path_length_tool,
    post_disaster_assessment_based_on_connectivity_tool,
    post_disaster_assessment_based_on_diameter_tool,
    post_disaster_assessment_based_on_global_network_efficiency_tool,
    post_disaster_assessment_based_on_node_accessibility_tool,
    during_recovery_assessment_of_betweenness_based_recovery_order_tool,
    during_recovery_assessment_of_node_degree_based_recovery_order_tool,
    during_recovery_assessment_of_propagation_ranges_based_recovery_order_tool,
    during_recovery_assessment_of_GA_derived_GSCC_based_recovery_order_tool,
    during_recovery_assessment_of_SA_derived_GSCC_based_recovery_order_tool,
    during_recovery_assessment_of_GA_derived_population_based_recovery_order_tool,
    during_recovery_assessment_of_SA_derived_population_based_recovery_order_tool,
    recovery_order_determined_based_on_betweenness_tool,
    recovery_order_determined_based_on_node_degree_tool,
    recovery_order_determined_based_on_propagation_ranges_tool,
    recovery_order_determined_based_on_GSCC_by_GA_tool,
    recovery_order_determined_based_on_GSCC_by_SA_tool,
    recovery_order_determined_based_on_population_by_GA_tool,
    recovery_order_determined_based_on_population_by_SA_tool,
    recovery_plan_determined_based_on_WCC_by_GA_tool,
    recovery_plan_determined_based_on_population_by_GA_tool,
    recovery_plan_determined_based_on_clustering_coefficient_tool,
    recovery_plan_determined_under_resource_constraints_tool,
    recovery_plan_determined_under_cost_constraints_tool
]

prompt_template = PromptTemplate(
    input_variables=["tools", "tool_names", "input", "agent_scratchpad"],
    template="""
You are an expert in interdependent infrastructure networks, and your task is to solve the problem step by step using the provided tools.
__________________________________________________________________
To solve a task, please use the following format:
Complete format:
Thought: (reflect on your progress and decide what to do next (based on observation if exist), do not skip)
Action: (the action name, should be one of [{tool_names}]. Decide the action based on previous Thought and Observation)
Action Input: (the input string to the action, decide the input based on previous Thought and Observation)
Observation: (the result of the action)
(this process can repeat, and you can only process one task at a time)

OR
Thought: (review original question and check my total process) 
Final Answer: (output the final answer to the original input question based on observation)
__________________________________________________________________

Answer the question below using the following tools: {tools} 
Use the tools provided, and use the most specific tool available for each action. Your final answer should contain all information necessary to answer the question and subquestions.
Question: {input}
__________________________________________________________________
REMEMBER:
1. You can only respond with a single complete "Thought, Action, Action Input, Observation" format OR a single "Final Answer" format.
2. Don't create files that don't exist yourself.
3. Before all actions begin, you need to first plan the overall execution steps to complete the task.
Begin!
Thought: {agent_scratchpad}"""
)

# Initialize the agent
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    prompt=prompt_template,
    callbacks=[process_logger]
)

# Run the task using the agent
df = pd.read_excel(r"C:\Users\26389\OneDrive\Desktop\Task.xlsx")
if 'agent response' not in df.columns:
    df['agent response'] = ''

for index, row in df.iterrows():
    question = row.get('Task description for agents', '')
    if not str(question).strip():
        break

    try:
        # 每个问题之前都重新初始化代理和日志记录器
        process_logger.reset()
        agent = initialize_agent(
            tools=tools,
            llm=llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            prompt=prompt_template,
            callbacks=[process_logger]
        )
        response = agent.invoke(question)
        process_log = "\n".join(process_logger.logs)
        combined_response = f"Process Details:\n{process_log}"
        df.at[index, 'agent response'] = combined_response
    except Exception as e:
        df.at[index, 'agent response'] = f"Error: {str(e)}"

output_file = r"C:\Users\26389\OneDrive\Desktop\NPP-ReAct-response.xlsx"
df.to_excel(output_file, index=False)
print(f"Responses saved to {output_file}")
