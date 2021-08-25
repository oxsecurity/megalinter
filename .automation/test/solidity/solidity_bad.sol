pragm.a solidity ^0.8.7;
contract HelloWorld {

   stringa public message;

   constructor(string memory" initMessage) public {
      message = initMessage
   }

   function update(string memory newMessage) public {
      message = newMessage;
      }
}