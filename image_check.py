# -*- coding: utf-8 -*- 

# 处理流程：解析源imageset的Contents.json --> 拷贝源imageset中的图片到目标imageset中，并且根据imageset的名称规范图片名称
# --> 拷贝源Content.json到目标imageset中，并且规范json中的filename字段

import os
import sys
import json
from pprint import pprint
import shutil
import argparse

# imagesDir = '/Users/canvasT/Documents/work/netease/code/iOS/moneykeeper/src/MoneyKeeper/MoneyKeeper/Images.xcassets';
# currentDir = os.path.abspath('.');
# targetDir = os.path.join(currentDir, 'ResultFolder');

def writeJsonFile(jsonFilePath, data):
    with open(jsonFilePath, 'w') as targetJsonFileObj:
        jsonString = json.dumps(data, sort_keys=True, indent=2, separators=(',', ' : '))
        targetJsonFileObj.write(jsonString)
        targetJsonFileObj.close()

def handleImageset(relatePath, setType, root, rootDir, targetDir):
    # imageset的绝对路径
    dirName = os.path.join(root, relatePath)
    imageName = relatePath.replace(setType, '')
    # 读取文件内容
    srcJsonFileName = os.path.join(dirName, 'Contents.json')
    
    # 相对路径
    relateDirName = dirName.replace(rootDir + '/', '')
    
    # 目标imageset绝对路径
    targetImagesetDir = os.path.join(targetDir, relateDirName)

    lackImagesetDir = targetImagesetDir.replace('TempTargetFolder', 'LackImagesetsFolder');
    
    # 直接拷贝
    if setType == '.launchimage' or setType == '.appiconset':
        shutil.copytree(dirName, targetImagesetDir);
        return;

    # 拷贝 .imageset文件夹
    os.makedirs(targetImagesetDir)
    
    # 目标imageset的Contents.json文件
    targetJsonFile = os.path.join(targetImagesetDir, 'Contents.json')

    isLack = 0;

    # 只读的方式打开源imageset的Contents.json文件
    with open(srcJsonFileName, 'r') as fileObj:
        # 转化为json对象
        data = json.load(fileObj)
        if 'images' in data:
            images = data['images']

            for image in images:
                # a@2x.png 目前只支持png
                targetImageName = imageName + '@' + image['scale'] + '.png'
                # if setType == '.appiconset':
                #     targetImageName = imageName + '_' + image['idiom'] + '_' + image['size'] + '@' + image['scale'] + '.png'
                targetImageFile = os.path.join(targetImagesetDir, targetImageName)
                if 'filename' in image:
                    srcImageFile = os.path.join(dirName, image['filename'])
                    if os.path.exists(srcImageFile):
                        shutil.copyfile(srcImageFile, targetImageFile)
                    else:
                        print 'lack:', targetImagesetDir;
                        isLack = 1;
                        
                # 用标准的文件名替换原先不规范的名称
                image['filename'] = targetImageName
        # 关闭文件
        fileObj.close()

        # 写目标imageset的Contents.json文件
        writeJsonFile(targetJsonFile, data);

    if isLack:
        shutil.copytree(targetImagesetDir, lackImagesetDir);

def main():
    newParser = argparse.ArgumentParser();
    newParser.add_argument("-s", "--source", dest="source_argparse", help="source folder path");
    # newParser.add_argument("-d", "--destination", dest="destination_argparse", help="destination folder path");
    args = newParser.parse_args();

    rootDir = args.source_argparse;
    # targetDir = args.destination_argparse;
    targetDir = './TempTargetFolder';
    if not rootDir:
        print 'require source and destination args';
        return;

    if os.path.exists(targetDir):
        shutil.rmtree(targetDir)
    os.makedirs(targetDir)

    shutil.copyfile(os.path.join(rootDir, 'Contents.json'), os.path.join(targetDir, 'Contents.json'));
        
    list_dirs = os.walk(rootDir)
    for root, dirs, files in list_dirs:
        for d in dirs:
            # 检测是否为.imageset类型的文件夹
            if '.imageset' in d:
                handleImageset(d, '.imageset', root, rootDir, targetDir);

            if '.appiconset' in d:
                print 'handle appiconset'
                handleImageset(d, '.appiconset', root, rootDir, targetDir);

            if '.launchimage' in d:
                print 'handle launchimage'
                handleImageset(d, '.launchimage', root, rootDir, targetDir);

            if '.imageset' not in d and '.appiconset' not in d and '.launchimage' not in d:
                dirName = os.path.join(root, d)
                
                # 相对路径
                relateDirName = dirName.replace(rootDir + '/', '')
                # 目标imageset绝对路径
                targetImagesetDir = os.path.join(targetDir, relateDirName)
                targetJsonFile = os.path.join(targetImagesetDir, 'Contents.json')
                os.makedirs(targetImagesetDir)
                data = {
                    "info" : {
                        "version" : 1,
                        "author" : "xcode"
                    }
                };
                writeJsonFile(targetJsonFile, data);

    shutil.rmtree(rootDir);
    shutil.copytree(targetDir, rootDir);
    shutil.rmtree(targetDir);

    print 'complete';


if __name__ == '__main__':
    main();
    