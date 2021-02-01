from PyPDF2 import PdfFileWriter, PdfFileReader, PdfFileMerger
import sys
import os
      
def merge(pdf_list):
  input_pdf = pdf_list[:-1]
  output_pdf = pdf_list[-1]
  # check file exists
  for pdf in input_pdf:
    if not os.path.exists(pdf):
      print("error: {} not exists".format(pdf))
      return False
  if os.path.exists(output_pdf):
    print("error output file {} already exists".format(output_pdf))

  merger = PdfFileMerger()
  for pdf in input_pdf:
    merger.append(open(pdf, 'rb'))

  with open(output_pdf, 'wb') as fout:
    merger.write(fout)

def split(input_pdf):
  if not os.path.exists(input_pdf):
    print("error. file {} not exists".format(input_pdf))
    return False

  inputpdf = PdfFileReader(open(input_pdf, "rb"))

  for i in range(inputpdf.numPages):
    output = PdfFileWriter()
    output.addPage(inputpdf.getPage(i))
    with open("{}-page{}.pdf".format(input_pdf, i), "wb") as outputStream:
      output.write(outputStream)

def extract(input_pdf, start, end):
  inputpdf = PdfFileReader(open(input_pdf, "rb"))
  input_name = os.path.splitext(input_pdf)[0]
  output = PdfFileWriter()
  output_name = "{}_{}-{}.pdf".format(input_name, start, end)
  outputStream = open(output_name, "wb")

  end = min(inputpdf.numPages+1,end+1)

  print("extract {} from page {} to page {} to file {}".format(input_pdf, start, end, output_name))
  for i in range(start, end):
    output.addPage(inputpdf.getPage(i-1))
  output.write(outputStream)

def insert(original_pdf_path, insert_pdf_path, index):
  if not os.path.exists(original_pdf_path):
    print("error: original pdf {} not exists".format(original_pdf_path))
    return False
  if not os.path.exists(insert_pdf_path):
    print("error: insert {} not exists".format(insert_pdf_path))
    return False

  org_pdf = PdfFileReader(original_pdf_path)
  insert_pdf = PdfFileReader(insert_pdf_path)

  new_pdf = PdfFileWriter()
  new_pdf.appendPagesFromReader(org_pdf)
  for page in insert_pdf.pages:
    new_pdf.insertPage(page, index)

  org_pdf_dir, org_pdf_ext = os.path.splitext(original_pdf_path)
  org_pdf_name = os.path.basename(org_pdf_dir)

  int_pdf_dir, int_pdf_ext = os.path.splitext(insert_pdf_path)
  int_pdf_name = os.path.basename(int_pdf_dir)

  output_path = "output"
  if not os.path.exists(output_path):
    os.mkdir(output_path)

  new_pdf_path = "{}{}{}+{}.pdf".format(output_path, os.path.sep, org_pdf_name, int_pdf_name)
  with open(new_pdf_path, "wb") as outputStream:
    new_pdf.write(outputStream)

##----------------------------------
def remove(input_pdf_path, start, end):
  if not os.path.exists(input_pdf_path):
    print("error: original pdf {} not exists".format(input_pdf_path))
    return False

  new_pdf = PdfFileWriter()
  input_pdf = PdfFileReader(input_pdf_path)
  new_page_num = 0
  for i in range(0, input_pdf.getNumPages(),1):
    if i < start -1 or i >= end:
      page = input_pdf.getPage(i)
      new_pdf.insertPage(page, new_page_num) # append
      new_page_num += 1
  
  output_path = "output"
  if not os.path.exists(output_path):
    os.mkdir(output_path)

  input_pdf_dir, input_pdf_ext = os.path.splitext(input_pdf_path)
  input_pdf_name = os.path.basename(input_pdf_dir)

  new_pdf_path = "{}{}{}.pdf".format(output_path, os.path.sep, input_pdf_name)
  with open(new_pdf_path, "wb") as outputStream:
    new_pdf.write(outputStream)

##----------------------------------
def replace(input_pdf_path, replace_pdf_path, index):
  if not os.path.exists(input_pdf_path):
    print("error: original pdf {} not exists".format(input_pdf_path))
    return False
  if not os.path.exists(replace_pdf_path):
    print("error: replace pdf {} not exists".format(replace_pdf_path))
    return False

  new_pdf = PdfFileWriter()
  input_pdf = PdfFileReader(input_pdf_path)
  replace_pdf = PdfFileReader(replace_pdf_path)

  if input_pdf.getNumPages() < index: 
    print("error: {} is greater than the number of pages of input pdf {}".format(index, input_pdf.getNumPages()))
    return False

  new_page_num = 0
  for i in range(0, input_pdf.getNumPages(),1):
    if i != index-1:
      page = input_pdf.getPage(i)
    else:
      page = replace_pdf.getPage(0)
    new_pdf.insertPage(page, new_page_num) # append
    new_page_num += 1

  output_path = "output"
  if not os.path.exists(output_path):
    os.mkdir(output_path)

  input_pdf_dir, input_pdf_ext = os.path.splitext(input_pdf_path)
  input_pdf_name = os.path.basename(input_pdf_dir)

  new_pdf_path = "{}{}{}.pdf".format(output_path, os.path.sep, input_pdf_name)
  with open(new_pdf_path, "wb") as outputStream:
    new_pdf.write(outputStream)

##----------------------------------
def help():
  print("{} ACTION <ip or subnet of the target> [range of the port]".format(sys.argv[0]))
  print("ACTION")
  print(" merge <pdf separated by space}")
  print(" split input.pdf")
  print(" extract input.pdf <start page>[:end page]")
  print(" insert original.pdf insert.pdf insertStartPage")
  print(" remove input.pdf <start page>[:end page]")
  print(" replace input.pdf replace.pdf pageNumber")
  
if __name__ == "__main__":
  if len(sys.argv) < 2:
    help()
    exit()
  if sys.argv[1] == "merge":
    if len(sys.argv) < 4:
      print("at least two pdf files to be merged")
      help()
      exit()
    else:
      merge(sys.argv[2:])

  elif sys.argv[1] == "split":
    if len(sys.argv) < 3:
      print("at least two pdf files to be merged")
      help()
      exit()
    else:
      split(sys.argv[2])

  elif sys.argv[1] == "extract":
    if len(sys.argv) < 4:
      help()
      exit()
    else:
      input_pdf = sys.argv[2]
      page_range = sys.argv[3].split(":")
      start = int(page_range[0]) 
      end = int(page_range[1]) if len(page_range) > 1 else start

      extract(input_pdf, start, end)

  elif sys.argv[1] == "insert":
    if len(sys.argv) < 5:
      help()
      exit()
    else:
      org_pdf = sys.argv[2]
      int_pdf = sys.argv[3]
      index = int(sys.argv[4])

      insert(org_pdf, int_pdf, index)
  
  elif sys.argv[1] == "remove":
    if len(sys.argv) < 4:
      help()
      exit()
    else:
      input_pdf = sys.argv[2]
      page_range = sys.argv[3].split(":")
      start = int(page_range[0]) 
      end = int(page_range[1]) if len(page_range) > 1 else start

      remove(input_pdf, start, end)

  elif sys.argv[1] == "replace":
    if len(sys.argv) < 5:
      help()
      exit()
    else:
      org_pdf = sys.argv[2]
      replace_pdf = sys.argv[3]
      index = int(sys.argv[4])

      replace(org_pdf, replace_pdf, index)