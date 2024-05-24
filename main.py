import asyncio
import spade
from spade import wait_until_finished
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour,OneShotBehaviour
from spade.agent import Agent
from spade.message import Message
from spade.template import Template

class Pemungut(Agent):
    class pemungutan(CyclicBehaviour):
        async def on_start(self):
            print("Melakukan pemungutan . . .")
            await asyncio.sleep(3)
            print("Menuju agen penampungan untuk menyetor sampah")
            self.counter = 0
            print("jeda: {} menit".format(self.counter))
            await asyncio.sleep(2)

        async def run(self):
            self.counter += 10
            print("jeda: {} menit".format(self.counter))
            if self.counter == 60:
                await asyncio.sleep(2)
                self.kill(exit_code=10)
                await self.agent.stop()
            
            await asyncio.sleep(3)
    
    async def setup(self):
        print("Agen pemungut started")
        b = self.pemungutan()
        self.add_behaviour(b)
   

class Penampung(Agent):
    class InformBehav(OneShotBehaviour):
        async def run(self):
            # print("InformBehav running")
            msg = Message(to="receiver@localhost")     # Instantiate the message
            msg.set_metadata("performative", "inform")  # Set the "inform" FIPA performative
            msg.body = "Sampah sudah penuh, bisa segera diambil"                    # Set the message content

            await self.send(msg)
            print("Message sent from Penampung to Pengangkut!")

            # stop agent from behaviour
            await self.agent.stop()

    async def setup(self):
        # print("SenderAgent started")
        b = self.InformBehav()
        self.add_behaviour(b)

class Pengangkut(Agent):
    class RecvBehav(OneShotBehaviour):
        async def run(self):
            # print("RecvBehav running")

            msg = await self.receive(timeout=10) # wait for a message for 10 seconds
            if msg:
                print(" ")
                print("Message received with content: {}".format(msg.body))
                print("....")
                print("Pengangkutan menuju lokasi agen penampung untuk melakukan pemungutan sampah dan membuangnya ke TPA terdekat")
                print(" ")
            else:
                print("Did not received any message after 10 seconds")

            # stop agent from behaviour
            await self.agent.stop()

    async def setup(self):
        # print("ReceiverAgent started")
        b = self.RecvBehav()
        template = Template()
        template.set_metadata("performative", "inform")
        self.add_behaviour(b, template)


async def main():
    for x in range (1,4):
        pemungut = Pemungut("rezam123@yax.im", "qwerty123")
        await pemungut.start()
        print("Menuju titik yang ingin dibersihkan")
        await wait_until_finished(pemungut)
        print("Storage penampung : {}/3".format(x))
        print(" ")
    
    pengangkut = Pengangkut("receiver@localhost", "qwerty123")
    await pengangkut.start(auto_register=True)
    # print("Receiver started")

    penampung = Penampung("sender@localhost", "qwerty123")
    await penampung.start(auto_register=True)
    # print("Sender started")

    await spade.wait_until_finished(pengangkut)
    print("Agents finished")

    

if __name__ == "__main__":
    spade.run(main())
