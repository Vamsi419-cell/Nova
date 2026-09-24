
import json

from pydantic import ValidationError

from nova.agent import (
    client,
    tools,
    tools_map,
    validation_map,
    output_validation_map,
    SYSTEM_PROMPT,
)


def run_agent(user_input):

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": user_input,
        },
    ]

    agent_log = []
    iteration = 0
    MAX_ITERATIONS = 10

    while True:

        iteration += 1

        if iteration > MAX_ITERATIONS:
            print("Maximum iterations reached. Stopping.")
            break

        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=messages,
            max_tokens=500,
            tools=tools,
            tool_choice="auto",
        )

        message = response.choices[0].message

        if message.tool_calls:

            messages.append(message)

            for tool_call in message.tool_calls:

                tool_name = tool_call.function.name

            

                try:
                    tool_args = json.loads(
                        tool_call.function.arguments
                    )

                except json.JSONDecodeError as e:

                    result = f"Error decoding JSON for tool {tool_name}: {e}"

                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": result,
                        }
                    )

                    agent_log.append(
                        {
                            "iteration": iteration,
                            "tool_name": tool_name,
                            "arguments": None,
                            "result": result,
                            "status": "input_error",
                        }
                    )

                    continue

               

                try:

                    validation = validation_map.get(tool_name)

                    validated_args = validation(**tool_args)

                except ValidationError as e:

                    result = (
                        f"Input validation error for "
                        f"{tool_name}: {e}"
                    )

                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": result,
                        }
                    )

                    agent_log.append(
                        {
                            "iteration": iteration,
                            "tool_name": tool_name,
                            "arguments": tool_args,
                            "result": result,
                            "status": "input_error",
                        }
                    )

                    continue



                try:

                    tool_function = tools_map.get(tool_name)

                    result = tool_function(
                        **validated_args.model_dump()
                    )

                except Exception as e:

                    result = (
                        f"Error executing tool "
                        f"{tool_name}: {e}"
                    )

                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": result,
                        }
                    )

                    agent_log.append(
                        {
                            "iteration": iteration,
                            "tool_name": tool_name,
                            "arguments": tool_args,
                            "result": result,
                            "status": "tool_error",
                        }
                    )

                    continue


                try:

                    output_validation = output_validation_map.get(
                        tool_name
                    )

                    validated_output = output_validation(
                        result=result
                    )

                except ValidationError as e:

                    result = (
                        f"Output validation error for "
                        f"{tool_name}: {e}"
                    )

                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": result,
                        }
                    )

                    agent_log.append(
                        {
                            "iteration": iteration,
                            "tool_name": tool_name,
                            "arguments": tool_args,
                            "result": result,
                            "status": "output_error",
                        }
                    )

                    continue


                result = validated_output.model_dump()

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result),
                    }
                )

                agent_log.append(
                    {
                        "iteration": iteration,
                        "tool_name": tool_name,
                        "arguments": tool_args,
                        "result": result,
                        "status": "success",
                    }
                )

        else:

            print(message.content)
            break

    with open("agent_log.json", "w") as f:
        json.dump(agent_log, f, indent=4)

