import Image
from vector import EasyVector
from processing import border_detection

class FeatureHandler(object):
    def __init__(self, strategy, training_dataset):
        self.strategy = strategy
        self.dataset = {}
        self.feature_names = set()
        for label, values in training_dataset.items():
            self.dataset[label] = self.__extract_vectors(values)
            for features in self.dataset[label]:
                self.feature_names.update(features)
        self.feature_names = list(self.feature_names)
        self.inverted_feature_names = {}
        for i,name in enumerate(self.feature_names):
            self.inverted_feature_names[name] = i

    def __extract_vectors(self, values):
        return map(self.strategy, values)

    def __format_vector(self, vector):
        new_item = [0.0]*len(self.feature_names)
        for feature_name in vector:
            feature_position = self.inverted_feature_names.get(feature_name )
            if feature_position is not None:
                new_item[feature_position] = vector[feature_name]
        return new_item

    def sklearn_format_train(self):
        labels = []
        vectors = []
        for label,values in self.dataset.items():
            for vector in values:
                vectors.append(self.__format_vector(vector))
                labels.append(label)
        return vectors,labels

    def sklearn_format_test(self, items):
        vecs = self.__extract_vectors(items)
        vectors = []
        for vector in vecs:
            vectors.append(self.__format_vector(vector))
        return vectors

def border(callback):
    return lambda image,features: callback(border_detection(image), features, prefix='border-')

def x_histogram(image, features, prefix=''):
    width,height = image.size
    for x in range(width):
        for y in range(height):
            features[prefix+"x-histogram-"+str(x)] += image.getpixel((x,y))

def y_histogram(image, features, prefix=''):
    width,height = image.size
    for y in range(height):
        for x in range(width):
            features[prefix+'y-histogram-'+str(y)] += image.getpixel((x,y))

def positions(image, features, prefix=''):
    width,height = image.size
    for x in range(width):
        for y in range(height):
            features[prefix+'pos-'+str(x*height + y)] += image.getpixel((x,y))

def number_of_whites(image, features, prefix=''):
    width,height = image.size
    for x in range(width):
        for y in range(height):
            if image.getpixel((x,y)) > 245:
                features[prefix+'number_of_whites'] += 1

def number_of_pixels(image, features, prefix=''):
    width,height = image.size
    for x in range(width):
        for y in range(height):
            features[prefix+'number_of_pixels'] += 1

def use_features(aggregate):
    def do(file_path):
        features = EasyVector()
        with open(file_path) as f:
            image = Image.open(f).convert("L")
            for feature in aggregate:
                feature(image, features)
        return features
    return do
