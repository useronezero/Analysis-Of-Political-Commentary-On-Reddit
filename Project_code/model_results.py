from vectored_data import vector_formation
from tensorflow import keras
import numpy as np

# loads and run the model to get results
def run_model_get_results(subname):
  cleaned_data,cleaned_data_5,vectored_data = vector_formation(subname)

  model = keras.models.load_model('glove-bi-lstm.h5')

  output = []
  for sen_vec in vectored_data:
    sen_vec_array = np.array(sen_vec)
    word_v ,sen_v  = sen_vec_array.shape
    if word_v > 30:
      sen_part = int(word_v/30)
      increment = 0
      results  = []
      for _ in range(sen_part):
        word_v = 30
        part_of_vec = sen_vec_array[increment : increment + 30 ].reshape(-1,word_v,sen_v)
        results.append(model.predict(part_of_vec))
        increment += 30
        right_sum = 0
        left_sum = 0
      for res in results:
        right_sum += res[0][0]
        left_sum += res[0][1]
      output.append([round(((right_sum/sen_part) * 100),2),round(((left_sum/sen_part) * 100),2)])
    else:
      sen_vec_3d = sen_vec_array.reshape(-1,word_v,sen_v)
      results = model.predict(sen_vec_3d)
      output.append([round(results[0][0] * 100, 2),round(results[0][1] * 100, 2)])

  cleaned_data_5["scores"] = output

  return(cleaned_data,cleaned_data_5)