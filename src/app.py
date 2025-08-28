import os
import asyncio
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv
from azure.ai.agents.models import ListSortOrder
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace
os.environ["AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED"] = "true" # False by default

load_dotenv()
tracer = trace.get_tracer(__name__)

project_client = AIProjectClient(
    credential=DefaultAzureCredential(),
    endpoint=os.environ["PROJECT_ENDPOINT"],
)

app_insights_connection_string = project_client.telemetry.get_application_insights_connection_string()
configure_azure_monitor(connection_string=f"InstrumentationKey={app_insights_connection_string}")

with tracer.start_as_current_span("example-tracing"):
    agent = project_client.agents.create_agent(
        model = "gpt-4.1",
        name = "agent1",
        instructions = "You are an agent that assists with various tasks."
    )

    print(f"Created agent, agent ID: {agent.id}")

    thread = project_client.agents.threads.create()
    print(f"Created thread, ID: {thread.id}")

    message = project_client.agents.messages.create(
        thread_id=thread.id,
        role="user",
        content="Hi Agent436"
    )

    run = project_client.agents.runs.create_and_process(
        thread_id=thread.id,
        agent_id=agent.id)

    if run.status == "failed":
        print(f"Run failed: {run.last_error}")
    else:
        messages = project_client.agents.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)

        for message in messages:
            if message.text_messages:
                print(f"{message.role}: {message.text_messages[-1].text.value}")