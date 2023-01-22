import os
import hashlib
import re
import xml.etree.ElementTree as et
import sys
import zipfile

def main():
    print("[Info] Deck Create ...")

    DECK_NAME = sys.argv[1]
    BACKCARD_NAME = "back"


    # 不要なファイル(Zip)の削除
    print("[Info] Remove Zip File ...")
    fileNameList = []
    for fileName in os.listdir("./"):
        if re.search("\.zip", fileName):
            os.remove(fileName)
        else:
            fileNameList.append(fileName)


    # ファイルの読み込みとハッシュ値の生成
    print("[Info] Read Files and Create Hash ...")

    fileDict = {}
    backName = ""
    backHash = ""
    for fileName in fileNameList:
        with open(fileName, "rb") as file:
            fileContent = file.read()
            fileContentHash = hashlib.sha256(fileContent).hexdigest()
            tmp = re.search("{}\..*".format(BACKCARD_NAME), fileName)
            if tmp:
                backName = tmp[0]
                backHash = fileContentHash
            else:
                fileDict[fileName] = fileContentHash


    # XMLの生成
    print("[Info] Create XML ...")
    cardStackAttrib = {"location.name":"table","location.x":"0","location.y":"0","posZ":"0","rotate":"0","zindex":"0","owner":"","isShowTotal":"true"}
    cardStack = et.Element("card-stack", cardStackAttrib)
    tree = et.ElementTree(element=cardStack)

    cardStackData = et.SubElement(cardStack, "data", {"name":"image"})
    et.SubElement(cardStackData, "data", {"type":"image", "name":"imageIdentifier"})

    cardStackCommon = et.SubElement(cardStack, "data", {"name":"common"})
    et.SubElement(cardStackCommon, "data", {"name": "name"}).text = DECK_NAME

    et.SubElement(cardStack, "data", {"name":"detail"})

    DEF_CARDNAME = "カード"
    DEF_CARDSIZE = "2"
    cardStackNode = et.SubElement(cardStack, "node", {"name":"cardRoot"})
    for fileHash in fileDict.values():
        cardStackNodeCard = et.SubElement(cardStackNode, "card", {"location.name":"table","location.x":"0","location.y":"0","posZ":"0", "state":"1", "rotate":"0", "owner":"", "zindex":"0"})
        cardStackNodeCardData = et.SubElement(cardStackNodeCard, "data", {"name":"card"})

        cardStackNodeCardDataImage = et.SubElement(cardStackNodeCardData, "data", {"name":"image"})
        et.SubElement(cardStackNodeCardDataImage, "data", {"type":"image", "name":"imageIdentifier"})
        et.SubElement(cardStackNodeCardDataImage, "data", {"type":"image", "name":"front"}).text = fileHash
        et.SubElement(cardStackNodeCardDataImage, "data", {"type":"image", "name":"back"}).text = backHash


        cardStackNodeCardDataCommon = et.SubElement(cardStackNodeCardData, "data", {"name":"common"})
        et.SubElement(cardStackNodeCardDataCommon, "data", {"name":"name"}).text = DEF_CARDNAME
        et.SubElement(cardStackNodeCardDataCommon, "data", {"name":"size"}).text = DEF_CARDSIZE

        et.SubElement(cardStackNodeCardData, "data", {"name":"detail"})

    XML_NAME = "data.xml"
    tree.write(XML_NAME)

    # ファイルの圧縮
    print("[Info] Create Zip ...")
    with zipfile.ZipFile("xml_{}.zip".format(DECK_NAME), "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(XML_NAME, XML_NAME)
        zf.write(backName, re.search(r'\..*', backName)[0])
        for fileName in fileDict.keys():
            ext = re.search(r'\..*', fileName)
            hash = fileDict[fileName]
            print("[Info] TargetFileName:{}, Hash:{} ".format(fileName, hash))
            zf.write(fileName, hash + ext[0])

    os.remove(XML_NAME)
    print("[Info] Deck Created!")


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("[Error] Bad Argument")
        print("Usage:python create_deck.py <DeckName>".format(__file__))
        exit(1)
    main()