# Socket Definition
- id values will be capital
- data fields is small and values will be boolean
- Messages sent will follow the format of message object
- "Messages" is the eventName
  
## Message Object 
- id: discribe about msg data meaning
- data: payload required
  
## Message 

## Starting 
- id: START 
- data: 
  - start_server : boolean

### User option
- id: OPTION
- data:
  - denoise : boolean
  - skull_strip : boolean
  - bias_correction : boolean

### Mri zip upload 
- id: MRI_ZIP_UPLOAD
- data:
  - uploaded : boolean

### Pet zip upload 
- id: PET_ZIP_UPLOAD
- data:
  - uploaded : boolean
  - url : str

> All Images should be in png format
### MRI images
- mri images must be converted to base64 format and should be sent before preprocessing to user by anthor task (multiprocessor)
- EventName : MRI
#### Object Defifition
- slice_no: int
- data: string (base64)

> object should be sent as json object 

### PET images
- pet images should be saved when genrating and those pet images must be converted to base64 format and should be sent when generating rest to user by anthor task (multiprocessor)
- EventName : PET
#### Object Defifition
- slice_no: int
- data: string (base64)

> object should be sent as json object

> After All images sent :-
### Mri image upload 
- id: MRI_IMG_UPLOAD
- data:
  - uploaded : boolean
  - total_slice_number : int
### Pet image upload 
- id: PET_IMG_UPLOAD
- data:
  - uploaded : boolean
  - total_slice_number : int

### Process status
> sent msg when each step completes (will be directly feed to componet )
- id: PROCESS_STATUS
- data:
  - denoise : boolean
  - skull_strip : boolean
  - bais_correction : boolean
  - upload_start : boolean
  - upload_end : boolean
  - preprocess_start : boolean
  - preprocess_end : boolean
  - generate_start : boolean
  - generate_end : boolean
  - saving_start : boolean
  - saving_end : boolean

### User downloaded zip
- id: DELETE_STATUS
- data:
  - delete : boolean
