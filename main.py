from scrapper import Scrapper
from csv_handler import CsvHandler, DATA_VECTOR_CSV_PATH
from data_conversion import DataVectorConverter


scrapper = Scrapper()
csv_handler = CsvHandler(scrapper)
data_vector_converter = DataVectorConverter(csv_handler)

# Tutaj dajesz ile meczy masz
# data_vector_converter.process_matches(10)
#
matches = csv_handler.get_matches_from_csv()
data_vectors = data_vector_converter.create_data_vector_based_on_matches(matches)
#
data_vector_converter.save_data_vectors_to_csv(data_vectors)
