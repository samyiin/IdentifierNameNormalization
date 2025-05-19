import json
import openai


class SemanticSoftwordParser:
    def __init__(self, openai_apikey, model="gpt-4.1-mini"):
        """

        :param openai_apikey:
        :param model: # I tested, on 2025.Apr.16, gpt-4.1-nano and gpt-4o-mini is still too stupid for this task...
        but gpt-4.1-mini seems to be smart enough for this, and it's cheap enough: 7.5k requests 5 dollars
        """
        self.model = model
        self.openai_apikey = openai_apikey

        # Load system prompt and function schema
        with open("Utils/sys_msg.txt", "r") as f:
            self.system_prompt = f.read()

        with open("Utils/function.txt", "r") as f:
            self.function_def = json.load(f)

        # the buffer to store tha latest reasoning process
        self.reasoning_process = None

    def check_response(self, response):
        """
        If I want to have good design, maybe this should be a rewrittable callback function. So everyone can define their version of check_response.
        Anyways, here we will assume that openai almost always give the correct json format with correct setup. If not we will have to check that too.
        But since it's he assistant api, let's trust it's smart enough.
        """
        # first check if the response completed
        if not response.choices[0].finish_reason == "function_call":
            return False

        # assume that the json format is correct down to every layer? I don't want to check the ENUM layer...
        try:
            func_args = response["choices"][0]["message"]["function_call"]["arguments"]
            structured_json = json.loads(func_args)
        except:
            return False

        # check if all the substrings connects to the original word
        reconstructed_softword = "".join(
            split_item["softword"] for split_item in structured_json['interpretation']['split'])
        if not reconstructed_softword == structured_json["hardword"]:
            return False

        # check if the gpt indeed didn't expand the dictionary words and single letters
        for split_item in structured_json['interpretation']["split"]:
            if split_item["type"] in ["dictionary", "single_letter"]:
                if split_item["expansion"] != split_item["softword"]:
                    return False

        # check if the joined expansion word is indeed the result
        reconstructed_result = " ".join(
            split_item["expansion"] for split_item in structured_json['interpretation']['split'])
        if not reconstructed_result == structured_json['interpretation']["result"]:
            return False

        # That's pretty much all the tests
        return True

    def query(self, hardword, hardword_context):
        # Set your OpenAI API key
        openai.api_key = self.openai_apikey

        # Prepare the message payload
        messages = [
            {"role": "system", "content": self.system_prompt},
            {
                "role": "user",
                "content": f"hardword: \"{hardword}\"\ncontext: {hardword_context}"
            }
        ]

        # Call the API
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=messages,
            functions=[self.function_def],
            function_call="auto",
            temperature=1.0  # this high temperature works, so why not.
        )

        return response

    def query_until_success(self, hardword, hardword_context, max_query_num=10):
        response = self.query(hardword, hardword_context)
        # if response failed
        timeout = 0
        while not self.check_response(response):
            response = self.query(hardword, hardword_context)
            timeout += 1
            if timeout > max_query_num:
                raise Exception(
                    "Query failed: Could be LLM made 10 mistake in a row, internet, openai updated their service, or invalid APIKEY...")
        return response

    def parse(self, hardword, hardword_context):
        """

        :param softword:
        :param soft_word_context: So far I pass in something like this:
             f'This word is used in the Python programming identifier name "{soft_word_context}".'
        :return:
        """
        response = self.query_until_success(hardword, hardword_context)

        # this is the structured result including split and expand
        func_args = response["choices"][0]["message"]["function_call"]["arguments"]
        structured_json = json.loads(func_args)

        # this is the reasoning process of LLM
        self.reasoning_process = response["choices"][0]["message"]["content"]

        return structured_json

    def get_reasoning_process(self):
        """
        Only call this after you parsed!!!And this will not store the history
        :return:
        """
        return self.reasoning_process
