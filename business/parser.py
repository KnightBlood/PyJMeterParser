import logging
import string
from itertools import product

from lxml import etree

from utils.helpers import keep_after_regex, keep_before_question_mark, keep_after_hash


class JMeterParser:
    def __init__(self, jmx_file, length, remove_header, pattern, replacement_frames):
        self.jmx_file = jmx_file
        self.test_elements = []
        self.remove_header = remove_header
        self.pattern = pattern
        self.replacement_frames = replacement_frames
        self.load_jmx(length)

    def load_jmx(self, length):
        try:
            tree = etree.parse(self.jmx_file)
            self.root = tree.getroot()
            transaction_counter = 0

            transaction_names = self.generate_transaction_names(length)

            for transaction_controller in self.root.xpath(".//TransactionController"):
                name = transaction_controller.get("testname")
                transaction_counter += 1

                if transaction_counter <= len(transaction_names):
                    transaction_name = transaction_names[transaction_counter - 1]
                    format_name = f"事务_{transaction_name}#{keep_after_hash(name)}"
                    transaction_controller.set("testname", format_name)
                    self.test_elements.append({
                        "type": "Transaction Controller",
                        "number": transaction_counter,
                        "formatted_name": format_name,
                    })

                http_counter = 1

                for http_element in transaction_controller.xpath("./following-sibling::hashTree[1]/HTTPSamplerProxy"):
                    if self.remove_header:
                        for hash_tree in http_element.xpath("./following-sibling::hashTree[1]"):
                            for header in hash_tree.xpath("./HeaderManager"):
                                if len(header):
                                    hash_tree.remove(header.getnext())
                                    hash_tree.remove(header)

                    if "receiveHeartBeat.do" in http_element.xpath("./stringProp[@name='HTTPSampler.path']"):
                        transaction_controller.remove(http_element)
                    else:
                        http_name = http_element.get("testname")
                        if self.pattern:
                            http_name = keep_after_regex(self.pattern, http_name)
                        http_formatted_name = f"{transaction_name}_{http_counter}#{keep_before_question_mark(keep_after_hash(http_name))}"
                        http_element.set("testname", http_formatted_name)
                        self.test_elements.append({
                            "type": "HTTP Request",
                            "number": http_counter,
                            "formatted_name": http_formatted_name,
                        })

                        url_prop_element = http_element.xpath("./stringProp[@name='HTTPSampler.path']")[0]
                        for old_value, new_value in self.replacement_frames:
                            url_prop_element.text = url_prop_element.text.replace(old_value, new_value)

                    http_counter += 1

        except Exception as e:
            logging.error(f"Error parsing JMX file: {e}")

    @staticmethod
    def generate_transaction_names(length=2):
        letters = string.ascii_uppercase
        return [''.join(combination) for combination in product(letters, repeat=length)]

    def save_jmx(self, output_file):
        try:
            tree = etree.ElementTree(self.root)
            tree.write(output_file, pretty_print=True, xml_declaration=True, encoding="UTF-8")
            return True
        except Exception as e:
            logging.error(f"Error saving JMX file: {e}")
            return False