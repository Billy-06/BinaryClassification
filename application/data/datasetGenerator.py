import numpy as np
from os import listdir, getlogin
from glob import glob
from time import time
import cv2
import matplotlib.pyplot as plt
from imutils import rotate_bound
from os.path import isfile

def draw_table(data, classes ,save_as="table",save_to="images"):
    """

    :param data:
    :param classes:
    :param save_as:
    :param save_to:
    :return:
    """
    result = [[precision(label, data),recall(label, data)] for label in range(len(classes))]
    columns = ["precision","recall"]
    colors = plt.cm.BuPu(np.linspace(0, 0.5, len(classes)))[::-1]
    plt.table(colWidths=[.3, .3], cellText=result, cellLoc='center',rowLabels=classes,rowColours=colors,colLabels=columns,loc='center')
    plt.axis('off')
    plt.savefig(save_to+'/'+save_as+'.png')
    plt.show()

def dataSetGenerator(path,resize=False,resize_to=224,percentage=100,dataAugmentation= False):
    """
    Generate a image dataSet from a picture dataSets

    the picture dataSets must be in the same structure to generate also labels

    example of pictureFolder: http://weegee.vision.ucmerced.edu/datasets/landuse.html

    picture dataSets
      |
      |----------class-1
      |        .   |-------image-1
      |        .   |         .
      |        .   |         .
      |        .   |         .
      |        .   |-------image-n
      |        .
      |-------class-n

    :param str path: the path for picture dataSets folder
    :param bool resize: choose resize the pictures or not
    :param int resize_to: the new size of pictures
    :param int or float percentage: how many pictures you want to get from this pictureFolder
    :param int or bool dataAugmentation: apply data Augmentation Strategy
    :return:give as tuple of images, labels , classes
    :rtype: tuple[object[numpy.ndarray],object[numpy.ndarray],object[numpy.ndarray]]
        """
    try:
        start_time = time()
        classes = listdir(path)
        image_list = []
        labels = []
        for classe in classes:
            for filename in glob(path+'/'+classe+'/*'):
                img = cv2.resize(cv2.imread(filename, cv2.COLOR_BGR2RGB),(resize_to, resize_to)) if resize else cv2.imread(filename, cv2.COLOR_BGR2RGB)
                image_list.append(img)
                label = np.zeros(len(classes))
                label[classes.index(classe)] = 1
                labels.append(label)
                if dataAugmentation:
                    for angle in np.arange(0, 360, 90):
                        rotated = rotate_bound(img, angle)
                        image_list.append(rotated)
                        labels.append(label)
                        image_list.append(np.fliplr(rotated))
                        labels.append(label)
        indice = np.random.permutation(len(image_list))[:int(len(image_list)*percentage/100)] if percentage != 100 else np.random.permutation(len(image_list))
        print("\n --- dataSet generated in  %s seconds --- \n" % (np.round(time()-start_time)))
        return np.array([image_list[x] for x in indice]),np.array([labels[x] for x in indice]),np.array(classes)

    except IOError as e:
            print("I/O error({}): {} \nlike : {}".format(e.errno, e.strerror,path))

def dataSetToNPY(path,SaveTo="DataSets",resize=True,resize_to=224,percentage=80,dataAugmentation= False):
    """
    Generate a image dataSet from a picture dataSets and save it in pny files for fast reading in teast and train

    the picture dataSets must be in the same structure to generate also labels

    example of pictureFolder: http://weegee.vision.ucmerced.edu/datasets/landuse.html

    picture dataSets
      |
      |----------class-1
      |        .   |-------image-1
      |        .   |         .
      |        .   |         .
      |        .   |         .
      |        .   |-------image-n
      |        .
      |-------class-n

    :param str path: the path for picture dataSets folder (/)
    :param str SaveTo: the path when we save dataSets (/)
    :param bool resize: choose resize the pictures or not
    :param int resize_to: the new size of pictures
    :param int or bool dataAugmentation: apply data Augmentation Strategy
    :param int or float percentage: how many pictures you want to get from this pictureFolder for training
    :return: return dataset in npy files for fast Test and Train
    """
    try:
        from os import mkdir
        from os.path import exists
        dataSet_name = path.replace('\\',"/").split("/")[-1]
        mkdir(SaveTo+"/"+dataSet_name) if not exists(SaveTo+"/"+dataSet_name) else None
        SaveTo = SaveTo+"/"+dataSet_name
        data,labels,classes = dataSetGenerator(path,resize,resize_to,100,dataAugmentation)
        indice = np.random.permutation(len(data))
        indice80 = indice[:int(len(data)*percentage/100)]
        indice20 = indice[int(len(data)*percentage/100):]
        np.save(SaveTo+"/"+dataSet_name+'_dataTrain.npy',[data[x] for x in indice80])
        np.save(SaveTo+"/"+dataSet_name+'_labelsTrain.npy',[labels[x] for x in indice80])
        np.save(SaveTo+"/"+dataSet_name+'_dataTest.npy',[data[x] for x in indice20])
        np.save(SaveTo+"/"+dataSet_name+'_labelsTest.npy',[labels[x] for x in indice20])
        np.save(SaveTo+"/"+dataSet_name+'_classes.npy',classes)
    except IOError as e:
            print("I/O error({}): {} \nlike : {}".format(e.errno, e.strerror,path))

def picShow(data,labels,classes,just=None,predict=None,autoClose = False, Save_as = "pic", save_to = "images"):
    """
    show a pictures and which class belong in one figure

    :param list[int or float] data: list of picture that you need to show
    :param list[int or float] labels: list of labels for this picture
    :param list[str] classes: list of classes for this picture
    :param int or None just: how much picture you want to show
    :param list[str] or None predict: the list of probability of picture for each class
    :param bool autoClose: auto close of plot window after seconds
    :return: a figure contain this picture
    """
    fig = plt.figure()
    if just is None: just = len(data)
    for i in range(1, just+1):
        true_out = classes[labels[i-1].argmax()] # the true class of picture i
        sub = fig.add_subplot( np.rint(np.sqrt(just)),np.ceil(np.sqrt(just)), i)
        title = "true: "+true_out
        color = 'black'
        if predict is not None:
            classIndex = predict[i-1].argmax()
            predict_out = classes[classIndex] #the predicted class of picture i
            title += " predicted: "+ str(round(predict[i-1][classIndex]*100,2)) + " " + predict_out
            color = 'green' if predict_out == true_out else 'red'
        #sub.set_title(title,color=color, fontsize=7, fontweight='bold', y=-0.2-sub.get_ylim()[0])
        sub.set_title(title,color=color, fontsize=7, fontweight='bold')
        sub.axis('off')
        sub.imshow(data[i-1], interpolation='nearest', aspect="auto")
        plt.savefig(save_to+'/'+Save_as+'.png')

    if autoClose:
        plt.show(0)
        plt.pause(10)
        plt.close()
    else:
        plt.show()



def plotFiles(*path, xlabel='# epochs', ylabel='Error and Accu',reduce_each = False, autoClose = False, ff = None, Save_as = "plot", save_to = "images"):
    """
    Read data files and show it all in one Charts figure

    :rtype: object
    :param list[str] or str path: the path for all the file who contain data to plot
    :param str xlabel: x axes label name
    :param str ylabel: y axes label name
    :param bool autoClose: auto close of plot window after seconds
    :param str Save_as: figure name of chart saved
    :param bool or int reduce_each: reduce the chart each a specific number
    :return: Show data graph of files
    """
    for _ in path:
        if isfile(_):
            with open(_) as f:
                data = [float(i.strip('\x00')) for i in f.read().split('\n')[:-1] if float(i.strip('\x00'))]
                resultat = []
                if reduce_each:
                    for i in range(1, len(data), reduce_each):
                        l = data[i - 1:reduce_each * i]
                        resultat.append(sum(l) / float(len(l)))
                else:
                    resultat = data
                label = ff if ff else f.name.replace("\\", '/').split("/")[-1].split(".")[0]
                plt.plot(resultat, label=label)

        else:
            print("I/O error({}): {} \nlike : {}".format(IOError.errno, IOError.strerror,_))

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend(loc='center left')
    plt.savefig(save_to+'/'+Save_as+'.png')
    if autoClose:
        plt.show(0)
        plt.pause(10)
        plt.close()
    else:
        plt.show()
def plotSubFiles(*path, xlabel='# epochs', ylabel='Error and Accu',reduce_each = False, autoClose = False):
    """
    Read data files and show it all in sub charts figure

    :rtype: object
    :param list[str] or str path: the path for all the file who contain data to plot
    :param str xlabel: x axes label name
    :param str ylabel: y axes label name
    :param bool autoClose: auto close of plot window after seconds
    :return: Show data graph of files
    """
    for _ in path:
        if isfile(_):
            with open(_) as f:
                data = [float(i.strip('\x00')) for i in f.read().split('\n')[:-1] if float(i.strip('\x00'))]
                resultat = []
                if reduce_each:
                    for i in range(1, len(data), reduce_each):
                        l = data[i - 1:reduce_each * i]
                        resultat.append(sum(l) / float(len(l)))
                else: resultat = data
                plt.plot(resultat, label=f.name.split("/")[-1])
        else:
            print("I/O error({}): {} \nlike : {}".format(IOError.errno, IOError.strerror,_))

    plt.ylabel(ylabel)
    plt.xlabel(xlabel)
    plt.legend(loc='center left')
    if autoClose:
        plt.show(0)
        plt.pause(10)
        plt.close()
    else:
        plt.show()

def saveArray(data,npy_path):
    """
    save array to file.npy
    :param list[int] data: data array to save
    :param str npy_path: the path of npy file for saving
    """
    try:
        y = np.load(npy_path) if isfile(npy_path) else []
        np.save(npy_path,np.append(y,data))
        print("file saved", npy_path)
        return npy_path
    except IOError as e:
        print("I/O error({}): {} \nlike : {}".format(e.errno, e.strerror,npy_path))

def txtToNpy(txt_path,npy_path):
    """
    convert file.txt to file.npy

    :param str txt_path: the path of text file to convert into npy
    :param str npy_path: the path of npy file for saving
    """
    try:
        with open(txt_path) as f:
            saveArray([float(i) for i in f.read().split('\n')[:-1]],npy_path)
    except IOError as e:
        print("I/O error({}): {} \nlike : {}".format(e.errno, e.strerror,txt_path))

def saveClasses(path,save_to,mode = 'w'):
    """
    read picture dataSets folder and save classes name in texty file

    picture dataSets
      |
      |----------class-1
      |        .   |-------image-1
      |        .   |         .
      |        .   |         .
      |        .   |         .
      |        .   |-------image-n
      |        .
      |-------class-n

    :param str path: the path for picture dataSets folder
    :param str save_to: path for the text file where you want save classes name
    :param str mode: mode writing in text file so => a = append and w = write
    :return None :
    """
    if mode != 'a': open(save_to, 'w')
    for classe in listdir(path):
        with open(save_to, 'a') as f:
                    f.write(classe+'\n')

def loadClasses(path):
    """
    load classes name from text file
    :param str path:the path for text file contain the classes name
    :return list[str]: retrun list of classes name
    """
    with open(path) as f:
        return f.read().split('\n')[:-1]

def getLabel(classe,classes):
    """
    Generate a label From lot of resources

     - path for text file contain the classes name
     - path for picture dataSets folder
     - list contain classes name
     - numpy array contain classes name

    :param str classe :the name of classe
    :param list[int] or list[str] or str or object[numpy.ndarray] classes: the path of text file or dataSet folder or list of integer or String
    :return list[int]: label in probability form [0,0,1,0] of shape (1,n)

    """
    if type(classes) is str:
        classes = loadClasses(classes) if isfile(classes) else listdir(classes)
    elif isinstance(classes,np.ndarray):
        classes =classes.tolist()
    label = np.zeros(len(classes))
    label[classes.index(classe)] = 1
    return [label]

def imread(path,resize=224):
    """
    read a picture

    :param str path :path for pictures or folder to read
    :param int resize: the new size of picture
    :return list[float]: list of picture of shape (n,height,width,channel)

    """
    if isfile(path):
        return [cv2.resize(cv2.imread(_, cv2.COLOR_BGR2RGB),(resize, resize)) for _ in [path]]
    else:
        return [cv2.resize(cv2.imread(path+"/"+_, cv2.COLOR_BGR2RGB),(resize, resize)) for _ in listdir(path)]

def append(data=list,to=str):
    """
    save list() to text File

    :param data: list() of Data to save
    :param to: text file Were you wnat to save Data
    """

    for _ in data:
        with open(to, 'a') as f:
            f.write(str(_)+"\n")
    del data[:]

def draw_confusion_matrix(data,classes,save_as="confusion_mat",save_to="images",as_prob=True):
    """

    :param data:
    :param classes:
    :param str save_as: name of file to save
    :param str save_to: path of folder to safe the picture
    :param str save_to: path of folder to safe the picture
    :param bool as_prob: transform data to probability
    :return:
    """
    if as_prob : data = matrix_to_prob(data)
    plt.matshow(data,cmap=plt.cm.Blues)
    for idx,i in enumerate(data):
        for jdx,j in enumerate(i):
            if as_prob : j *= 100
            plt.text(idx, jdx, int(j), va='center', ha='center')
            plt.xticks(range(len(classes)),classes,rotation=270)
            plt.yticks(range(len(classes)),classes)
    plt.savefig(save_to+'/'+save_as+'.png')
    plt.show()

def confusion_matrix(softmax,labels,classes):
    """

    :param softmax:
    :param labels:
    :param classes:
    :return:
    """
    conf_mat = np.zeros((len(classes),len(classes)))
    for i,ite in enumerate(softmax):
        row = np.zeros(len(classes))
        row[np.argmax(ite)] = 1
        conf_mat[np.argmax(labels[i])] += row
    return conf_mat

def matrix_to_prob(conf_mat):
    """
    transform a matrix to probabilite
    :param object[numpy.ndarray] confusion_matrix: confusion matrix
    :return:
    """
    result = np.zeros((len(conf_mat),len(conf_mat[0])))
    for i,line in enumerate(conf_mat):
        moy = sum(line)
        for j,col in enumerate(line):
            result[i][j] = col/moy
    print(result)
    return result

def precision(label, confusion_matrix):
    col = confusion_matrix[:,label]
    return np.round(confusion_matrix[label][label] / sum(col),3)

def recall(label, confusion_matrix):
    """
    get recall
    :param list label: label as binary array
    :param object[numpy.ndarray] confusion_matrix: confusion matrix
    :return:
    """

    row = confusion_matrix[label,:]
    return np.round(confusion_matrix[label][label] / sum(row),3)

def precision_macro_average(confusion_matrix):
    """
    get precision macro average
    :param object[numpy.ndarray] confusion_matrix: confusion matrix
    :return:
    """
    rows, columns = confusion_matrix.shape
    sum_of_precisions = 0
    for label in range(rows):
        sum_of_precisions += precision(label, confusion_matrix)
    return sum_of_precisions / rows

def recall_macro_average(confusion_matrix):
    """
    get recall macro average
    :param object[numpy.ndarray] confusion_matrix: confusion matrix
    :return:
    """
    rows, columns = confusion_matrix.shape
    sum_of_recalls = 0
    for label in range(columns):
        sum_of_recalls += recall(label, confusion_matrix)
    return sum_of_recalls / columns
def accuracy(confusion_matrix):
    diagonal_sum = confusion_matrix.trace()
    sum_of_all_elements = confusion_matrix.sum()
    return diagonal_sum / sum_of_all_elements

if __name__ == '__main__':

    import argparse
    from textwrap import dedent

    parser = argparse.ArgumentParser(prog="Data Generator",formatter_class=argparse.RawDescriptionHelpFormatter,description=dedent('''image dataSet as numpy file.
    
       picture dataSets
          |
          |----------class-1
          |        .   |-------image-1
          |        .   |         .
          |        .   |         .
          |        .   |         .
          |        .   |-------image-n
          |        .
          |-------class-n
          
    '''))

    parser.add_argument('--path', metavar='path', type=str,required=True,
                        help='the path for picture dataSets folder (/)')
    parser.add_argument('--SaveTo', metavar='SaveTo', type=str, default="DataSets", help='the path when we save dataSet (/)')
    parser.add_argument('--resize', metavar='resize', type=bool, default=False,
                        help='choose resize the pictures or not')
    parser.add_argument('--resize_to', metavar='resize_to', type=int, default=224,
                        help='the new size of pictures')
    parser.add_argument('--percentage', metavar='percentage', type=int, default=80,
                        help='how many pictures you want to use for training')
    parser.add_argument('--dataAug', metavar='dataAugmentation', type=bool, default=False,
                        help='apply data Augmentation Strategy')

    args = parser.parse_args()

    dataSetToNPY(args.path, args.SaveTo,  args.resize,  args.resize_to,  args.percentage,  args.dataAug)