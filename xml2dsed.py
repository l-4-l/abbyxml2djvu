#!/usr/bin/python
# -*- coding: utf-8  -*-


from bs4 import BeautifulSoup
import lxml, pickle, re,sys
from os import system,listdir,getcwd,path

# variabili globali
'{{}}'
imgSize=[]
IAid=""
p=[]

def leggi(iaid, djvu):
    global IAid
    IAid=iaid
    global djvuName
    djvuName=djvu
    dump(djvu)
    global p
    if path.isfile(iaid+"_djvu.xml"):
        xml=open(iaid+"_djvu.xml","rb").read()
        while '<WORD coords="0,0,0,0' in xml:
            errore=find_stringa(xml,'<WORD coords="0,0,0,0',"</WORD>",1)
            print errore
            xml=xml.replace(errore,"")
            open(iaid+"_djvu.xml","wb").write(xml)
        p=coord(xml,"<OBJECT","</OBJECT>")
        salva_pcl(p,iaid,"")
    else:
        print "nessun file utilizzabile"
    return


def dump(djvuFile):
    global imgSize
    command="djvudump -o dump.txt %s" % (djvuFile)
    result=system(command)
    if result !=0:
        print "Errore in dump()"
        return
    d=open("dump.txt").read()
    imgSize=re.findall("DjVu (\d+)x(\d+)",d)
    return
    


# estrae una pagina (oggetto soup) dal file djvu.xml letto con leggi()
def pagina(n):
    f=open(IAid+"_djvu.xml","rb")
    f.seek(p[n][0])
    testo=f.read(p[n][1])
    bsPagina=BeautifulSoup(unicode(testo,"utf-8"),"xml")
    f.close()
    return bsPagina


# estrae il testo di una pagina, oggetto soup ottenuto con pagina()
def testoPag(soupPage):
    testo=""
    par=soupPage.find_all("PARAGRAPH")
    for i in par:
        lin=i.find_all("LINE")
        for l in lin:
            word=l.find_all("WORD")
            tl=[]
            for w in word:
                tl.append(w.get_text())
            tl=" ".join(tl)
            tl=tl.strip()
            testo+=tl+"\n"
        testo+="\n"
    return testo




def x2d(n):
    testo=""
    pag=pagina(n)
    if len(pag.find_all("OBJECT"))==0:
        return testo
    global imgSize
        
        
    testo="(page #### "
    width=int(pag.OBJECT["width"])
    height=int(pag.OBJECT["height"])
    for col in pag.find_all("PAGECOLUMN"):
        if len(col.find_all("WORD"))>0:
            testocol="\n (column #### "
            for reg in col.find_all("REGION"):
                if len(reg.find_all("WORD"))>0:
                    testoreg="\n  (region #### "
                    for par in reg.find_all("PARAGRAPH"):
                        if len(par.find_all("WORD"))>0:

                            testopar="\n   (para #### "
                            for lin in par.find_all("LINE"):
                                testolinea="\n    (line #### "
                                maxcoord="100000 100000 0 0"
                                for word in lin.find_all("WORD"):
                                    coord,maxcoord=xy(word["coords"],height,maxcoord,hpage=int(imgSize[n][1]))
                                    testoWord=replacer(word.get_text()) #.replace("\\",";").replace('"',r"'")

                                    testolinea+='\n     (word %s "%s")' % (coord,testoWord)
                                testolinea=testolinea.replace("####",rect(re.findall("word (\d+ \d+ \d+ \d+)",testolinea)))
                                testolinea+=")"
                                testopar+=testolinea
                            testopar=testopar.replace("####",rect(re.findall("line (\d+ \d+ \d+ \d+)",testopar)))                       
                            testopar+=")"
                            testoreg+=testopar
                    testoreg=testoreg.replace("####",rect(re.findall("para (\d+ \d+ \d+ \d+)",testoreg)))                            
                    testoreg+=")"
                    testocol+=testoreg
            testocol=testocol.replace("####",rect(re.findall("region (\d+ \d+ \d+ \d+)",testocol)))
            testocol+=")"
            testo+=testocol
    testo=testo.replace("####",rect(re.findall("column (\d+ \d+ \d+ \d+)",testo)))
    testo+=")"
    testo=testo.replace("\n (column #### )","").replace("\n (column 0 0 0 0 )","")
    return testo

def dsed(ini=None,fin=None):
    dsedFile="select\nremove-txt\n"
    if ini==None:
        ini=0
    if fin==None:
        fin=len(p)
    for i in range(ini,fin):
        testo=x2d(i)
        if testo!="":
            testo="select %d\nset-txt\n" % (i+1)+testo+"\n.\n"
            dsedFile+=testo
        print "pagina: ",i+1, "bytes:",len(testo)
    open("output.dsed","w").write(dsedFile.encode("utf-8"))
    open("%s.dsed" % (IAid),"w").write(dsedFile.encode("utf-8"))
    result=system('djvused %s -f output.dsed -s' % djvuName)
    if result==0:
        print "dsed caricato"
        djvuFix(djvuName)
    return
        
        
def replacer(testo):
    testo=testo.replace("\\",";")\
           .replace("'",u"\u2019")\
           .replace('"',r"'")\
           .replace(u"\xf9",u"\xfa")\
           .replace(u"\xec",u"\xed")\
           .replace("cosi",u"cos\xed")\
           .replace(u"\xe0",u"\xe1")
    return testo




def rect(lista):
    
    if lista==[]:
        return "0 0 0 0"
    for i in range(len(lista)):
        x=lista[i].split(" ")
        for j in range(len(x)):
            x[j]=int(x[j])
            lista[i]=x
    result=lista[0]
    for i in range(1,len(lista)):
        result[0]=min(result[0],lista[i][0])
        result[1]=min(result[1],lista[i][1])
        result[2]=max(result[2],lista[i][2])
        result[3]=max(result[3],lista[i][3])
    result="%d %d %d %d" % (result[0],result[1],result[2],result[3])
    return result


def xy(coords,height,maxcoord,hpage):
	
    fact=hpage*1.0/height
    coords=coords.split(",")[:4]
    coords[0]=str(int((int(coords[0]))*fact))
    coords[1]=str(int((height-int(coords[1]))*fact))
    coords[2]=str(int((int(coords[2]))*fact))
    coords[3]=str(int((height-int(coords[3]))*fact))

    maxcoord=maxcoord.split(" ")
    maxcoord[0]=str(min(int(maxcoord[0]),int(coords[0])))
    maxcoord[1]=str(min(int(maxcoord[1]),int(coords[1])))
    maxcoord[2]=str(max(int(maxcoord[2]),int(coords[2])))
    maxcoord[3]=str(max(int(maxcoord[3]),int(coords[3]))) 

    return (" ".join(coords)," ".join(maxcoord))
    
                        
    
def childr(el):
    for i in el.children:
        if i.name != None:
            print i.name,
            if "coords" in i.attrs:
                print i["coords"], i.get_text()
            print
            childr(i)
    return

def djvuFix(djvu):
    command="djvutxt %s -detail=page test.txt" % (djvu)
    result=system(command)
    if result != 0:
        print "errore in djvutxt"
        return
    f=open("test.txt").read().split("\n")
    n=1
    failed=[]
    l=[]
    for i in range(len(f)):
        if f[i].startswith("(page "):
            n+=1
        elif f[i].startswith("()"):
            n+=1
        elif f[i].startswith("failed"):
            l.append(n)
            n+=1
    print l
    if len(l)>0:
        for page in l:
            result=system('djvused %s -e "select %d; output-txt">dummy.txt' % (djvu,page))
            if result==10:
                result=system('djvused %s -e "select %d; remove-txt; save"' % (djvu,page))
                "Testo pagina ",page," corrotto, viene cancellato"
    return
    


    
    
# this finds offset and length of elements <page...>...</page> into abbyy xml file
def coord(f,s1,s2):
    l=[]
    d1=0
    while True:
        d1=f.find(s1,d1)
        if d1==-1:
            break
        d2=f.find(s2,d1)
        l.append((d1,d2+len(s2)-d1))
        d1=d2
    return l


        
### pickle utilities 

def carica_pcl(nome_file, folder="dati/"):
    nome_file=folder+nome_file+".pcl"
    f=open(nome_file)
    contenuto=pickle.load(f)
    f.close()
    return contenuto

def salva_pcl(variabile,nome_file="dato",folder="dati/"):
    nome_file=folder+nome_file+".pcl"
    f=open(nome_file,"w")
    pickle.dump(variabile, f)
    f.close()
    print "Variabile salvata nel file "+nome_file
    return



def find_stringa(stringa,idi,idf,dc=0,x=None,side="left"):
    if side=="right":
        idip=stringa.rfind(idi)
    else:
        idip=stringa.find(idi)
    idfp=stringa.find(idf,idip+len(idi))+len(idf)
    if idip>-1 and idfp>0:
        if x!=None:
            while stringa[idip:idfp].count(x)>stringa[idip:idfp].count(idf):
                if stringa[idip:idfp].count(x)>stringa[idip:idfp].count(idf):
                    idfp=stringa.find(idf,idfp)+len(idf)
                
        if dc==0:
            vvalore=stringa[idip+len(idi):idfp-len(idf)]
        else:
            vvalore=stringa[idip:idfp]
    else:
        vvalore=""
    return vvalore

def produci_lista(testo,idi,idf,dc=1,inizio=None):
    t=testo[:]
    lista=[]
    while not find_stringa(t,idi,idf,1,inizio)=="":
        el=find_stringa(t,idi,idf,1,inizio)
        t=t.replace(el,"",1)
        if dc==0:
            el=find_stringa(el,idi,idf,0,inizio)
        lista.append(el)
    return lista



def main(params):
    leggi(params[1],params[2])
    dsed()
    return

if __name__ == "__main__":

    djvu=sys.argv
    main(djvu)

